import datetime
import glob
import io
import os
import re
import time
import traceback

from astropy.io import fits
import multiprocessing as mp
import numpy
import psycopg2
import psycopg2.extras

import ecallisto.sources.fits_sampler
import ecallisto.sources.instruments
import ecallisto.sources.stations

import skyfield
from skyfield.api import load
from datetime import timezone
from skyfield.api import N, W, wgs84
from skyfield import almanac

import ecallisto.configs.ecallisto_config as ecallisto_config


class FitsImporter:

    def __init__(self, start_date, end_date, delete_related_tiles=True):
        database = self.get_db()
        self.amount_threads = 20

        # round to full day
        self.start_date = datetime.datetime.combine(start_date.date(), datetime.time.min)
        self.end_date = datetime.datetime.combine(end_date.date(), datetime.time.min)

        manager = mp.Manager()
        self.instruments = manager.list()
        self.virtual_instruments = manager.list()
        self.stations = manager.list()

        self.__get_instruments_and_virtual_instruments(database)
        self.__get_stations(database)
        self.delete_related_tiles = delete_related_tiles

        # multiprocessing queue
        self.fits_queue = mp.Queue()

        # multiprocessing manager list

        self.missing_instruments = manager.dict()
        self.missing_virtual_instruments = manager.dict()
        self.missing_stations = manager.dict()
        self.tile_remove = manager.dict()
        self.value_strings = manager.list()

        self.procs = list()

        # creating processes
        for i in range(self.amount_threads):
            p = mp.Process(target=self.__import_directory_fits)
            self.procs.append(p)
            p.start()

    def run(self):
        print("Importing data from %s - %s" % (self.start_date, self.end_date))
        while self.end_date >= self.start_date:
            day_directory = os.path.join(ecallisto_config.DATA_PATH,
                                         "%04d" % self.end_date.year,
                                         "%02d" % self.end_date.month,
                                         "%02d" % self.end_date.day)

            if os.path.exists(day_directory):
                fits_files = self.__get_unregistered_fits_files(day_directory)
                [self.fits_queue.put(file) for file in fits_files]

                # child_run() processor with function '__import_directory_fits'
                while self.fits_queue.qsize() != 0:
                    time.sleep(1)  # sleep for one second

                # self.__delete_tiles()
                if len(self.value_strings):
                    self.__bulk_insert_day()

                # handle missing information such as instruments, virtual_instruments and stations
                self.__handle_missing_data()

                # update new changes from data in DB
                self.__update_instruments()
                self.__add_new_virtual_instruments_in_db()
                self.__update_stations()

            self.end_date -= datetime.timedelta(days=1)

        # clean up, exit processes gracefully
        [self.fits_queue.put("END") for i in range(self.amount_threads)]
        print("Imported all data from %s - %s" % (self.start_date, self.end_date))

        for proc in self.procs:
            proc.join()

        # clean exit

    # update meta data of each station
    def __update_stations(self):
        database = self.get_db()
        current_date = self.end_date
        cursor = database.cursor()
        for station in self.stations:
            if not station["updated"]:
                continue

            obs_lon = station["obs_lon"]
            obs_lat = station["obs_lat"]

            # calculate ephemeris times
            ephemeris_start, ephemeris_end = self.__calculate_ephemeris(current_date, obs_lon, obs_lat)

            observation_start, observation_end = None, None
            if ephemeris_start is not None or ephemeris_end is not None:
                # get observation times and update observational_data table
                observation_start, observation_end = self.__get_observation_times(station, ephemeris_start,
                                                                                  ephemeris_end)

            max_observation_time = None
            actual_observation_time = None
            duration = None
            if ephemeris_start is not None and ephemeris_end is not None and observation_start is not None and observation_end is not None:
                max_observation_time = ephemeris_end - ephemeris_start
                actual_observation_time = observation_end - observation_start
                duration = max_observation_time - actual_observation_time

            # update station meta data
            sql_update_instr = """UPDATE stations SET ephemeris_start=%s, ephemeris_end=%s, observation_start=%s, 
                            observation_end=%s, obs_lon=%s, obs_lat=%s, max_observation_time=%s, actual_observation_time=%s, 
                            duration=%s WHERE id=%s"""

            cursor.execute(sql_update_instr, (
                ephemeris_start,
                ephemeris_end,
                observation_start,
                observation_end,
                obs_lon,
                obs_lat,
                datetime.datetime.strptime(str(max_observation_time),
                                           "%H:%M:%S").time() if max_observation_time is not None else None,
                datetime.datetime.strptime(str(actual_observation_time),
                                           "%H:%M:%S").time() if actual_observation_time is not None else None,
                datetime.datetime.strptime(str(duration), "%H:%M:%S").time() if duration is not None else None,
                station["id"]
            ))

            station["updated"] = False
        database.commit()
        cursor.close()

    def __get_regex_pattern(self, file_name):
        # STATION-NAME_yyyyMMdd_HHmmss_INSTRUMENT-NUMBER
        # ALASKA-ANCHORAGE_20210429_000000_59
        pattern = re.compile("^[A-z|0-9|-]+_\\d{8}_\\d{6}_\\d{2}")

        # STATION-NAME_yyyyMMdd_HHmmssCHARS
        # PHOENIX-2_20060621_080000i
        # PHOENIX-2_20001023_063000l1
        pattern_b = re.compile("^[A-z|0-9|-]+_\d{8}_\d{6}[A-z|0-9]+")
        if pattern.search(file_name):
            # pattern did match!
            file_name_splitted = re.split("_", file_name)

            regex_pattern = file_name_splitted[0] + "_\d{8}_\d{6}_" + file_name_splitted[3]
            instrument_name = file_name_splitted[0] + "_" + file_name_splitted[3]
            return regex_pattern, instrument_name
        elif pattern_b.search(file_name):
            # pattern did match!
            file_name_splitted = re.split("_", file_name)
            temp_pattern = re.compile("([0-9]+)([a-zA-Z0-9]+)")
            result_grouped = temp_pattern.match(file_name_splitted[2]).groups()
            regex_pattern = file_name_splitted[0] + "_\d{8}_\d{6}" + result_grouped[1]
            instrument_name = file_name_splitted[0] + "_" + result_grouped[1]
            return regex_pattern, instrument_name

        return None, None

    def __handle_missing_data(self):
        # handle missing instruments and stations
        for station_name, current_fits_file in self.missing_instruments.items():
            file_name = current_fits_file.rsplit('/', 1)[1]
            file_name_ending = file_name.split('.', 1)
            file_name = file_name_ending[0]
            file_ending = "." + file_name_ending[1]
            regex_pattern, instrument_name = self.__get_regex_pattern(file_name)

            if instrument_name is None:
                print("Warning: Could not import file '%s' since no matching regex was found" % current_fits_file)
                return None, None

            try:
                instrument = self.__add_new_instrument(current_fits_file, regex_pattern + file_ending, instrument_name)
                self.instruments.append(instrument)
            except Exception as e:
                print(e)
                print("BUG")
        self.missing_instruments.clear()

        for station_name, current_virtual_instrument in self.missing_virtual_instruments.items():
            virtual_instrument = self.__add_new_virtual_instrument(current_virtual_instrument)
            self.virtual_instruments.append(virtual_instrument)
        self.missing_virtual_instruments.clear()

        for current_station_name, _ in self.missing_stations.items():
            # Either there is no entry in the stations table or there is just no reference yet to the instruments table
            station = self.__add_new_station(current_station_name)
            self.stations.append(station)
        self.missing_stations.clear()

    def __add_virtual_instruments(self, virtual_instrument):
        database = self.get_db()
        cursor = database.cursor()
        sql_insert_instr = """INSERT INTO virtual_instruments (fk_instrument, frequencies) VALUES (%s, %s)"""
        cursor.execute(sql_insert_instr, (
            virtual_instrument['instrument_id'],
            virtual_instrument['frequencies']
        ))

        database.commit()
        cursor.close()

    def __get_observation_times(self, station, ephemeris_start, ephemeris_end):
        database = self.get_db()
        sql_select_dates = """SELECT f.observation_times FROM fits f LEFT JOIN virtual_instruments v ON f.fk_virtual_instrument = v.id LEFT JOIN instruments i ON v.fk_instrument = i.id LEFT JOIN stations s ON i.fk_station = s.id WHERE s.id=%s AND %s && observation_times ORDER BY observation_times;"""
        with database.cursor() as cursor:
            sql_str = cursor.mogrify(
                sql_select_dates, (
                    station["id"],
                    psycopg2.extras.DateTimeRange(ephemeris_start, ephemeris_end, "()")
                )
            )
            cursor.execute(sql_str)
            observations_times_list = cursor.fetchall()
            observations_times = [x[0] for x in observations_times_list]
        cursor.close()
        if observations_times is None or len(observations_times) == 0:
            return None, None
        observation_start = observations_times[0].lower
        observation_end = observations_times[len(observations_times) - 1].upper

        return observation_start, observation_end

    def __calculate_ephemeris(self, current_date, obs_longitude, obs_latitude):
        # ephemeris_time_start = sunrise
        # ephemeris_time_end = sunset

        previous_day = current_date - datetime.timedelta(days=1)
        next_date = current_date + datetime.timedelta(days=1)
        ts = load.timescale()
        previous_day_utc = previous_day.replace(tzinfo=timezone.utc)
        next_day_utc = next_date.replace(tzinfo=timezone.utc)
        t0 = ts.from_datetime(previous_day_utc)
        t1 = ts.from_datetime(next_day_utc)
        eph = load('de421.bsp')  # ephemeris DE421
        bluffton = wgs84.latlon(obs_latitude * N, obs_longitude * W)
        t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, bluffton))

        # There are cases where no sunrise and sunset information are available on a certain date
        if y is None or y.size == 0:
            return None, None

        # y => 1 = sunrise, 0 = sunset
        ephemeris_start = datetime.datetime.strptime(t[1].utc_iso(), "%Y-%m-%dT%H:%M:%SZ")
        ephemeris_end = datetime.datetime.strptime(t[2].utc_iso(), "%Y-%m-%dT%H:%M:%SZ")

        return ephemeris_start, ephemeris_end

    def __get_observations_times(self, station, current_date):
        database = self.get_db()
        next_day = current_date + datetime.timedelta(days=1)
        sql_select_dates = """SELECT f.observation_times FROM fits f LEFT JOIN virtual_instruments v ON f.fk_virtual_instrument = v.id LEFT JOIN instruments i ON v.fk_instrument = i.id LEFT JOIN stations s ON i.fk_station = s.id WHERE s.id=%s AND %s && observation_times ORDER BY observation_times;"""
        with database.cursor() as cursor:
            sql_str = cursor.mogrify(
                sql_select_dates, (
                    station["id"],
                    psycopg2.extras.DateTimeRange(current_date, next_day, "()")
                )
            )
            cursor.execute(sql_str)
            observations_times_list = cursor.fetchall()
            observations_times = [x[0] for x in observations_times_list]
        cursor.close()
        observation_time_start = observations_times[0].lower
        observation_time_end = observations_times[len(observations_times) - 1].upper

        return observation_time_start, observation_time_end

    def __delete_tiles(self):
        database = self.get_db()
        with database.cursor() as cursor:
            # invalidate generated tiles
            sql_delete_tiles = """DELETE FROM images WHERE fk_virtual_instrument = %s AND tree_level = %s AND tree_index IN %s"""
            for virtual_instrument_id in self.tile_remove:
                for level, indices in enumerate(self.tile_remove[virtual_instrument_id]):
                    cursor.execute(sql_delete_tiles, (virtual_instrument_id, level, tuple(indices)))
        self.tile_remove.clear()
        database.commit()

    # insert new fits data
    def __bulk_insert_day(self):
        database = self.get_db()
        with database.cursor() as cursor:
            # bulk insert day
            all_values = "\n".join(self.value_strings)
            value_file = io.StringIO(all_values.replace("\\", "\\\\"))

            try:
                cursor.copy_from(value_file, "fits", sep="\t",
                                 columns=("fk_virtual_instrument", "import_date", "observation_times", "path"))
            except Exception as e:
                # ignore, since fits path in 'path' already exists
                print("Error copy_from")
                print(e)
                pass

        self.value_strings[:] = []
        database.commit()

    def __add_new_instrument(self, fits_file, regex_pattern, instrument_name):
        # hdulist checks
        hdulist = None
        try:
            hdulist = fits.open(fits_file)
        except Exception:
            print("Warning: Could not import file '%s' since there is an error while reading the file" % fits_file)
            if hdulist is not None:
                hdulist.close()

        origin = hdulist[0].header["ORIGIN"]
        sql_query = """INSERT INTO instruments (regex, location, origin, instrument_name) VALUES (%s, %s, %s, %s) RETURNING id, fk_station, regex, location, origin, instrument_name, start_data, end_data;"""

        database = self.get_db()
        with database.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                sql_query, (
                    regex_pattern,
                    None,
                    origin,
                    instrument_name
                )
            )
            instrument = dict(cursor.fetchone())
        database.commit()
        cursor.close()

        label = "%s, %s" % (instrument["instrument_name"], instrument["location"])
        instrument["label"] = label
        instrument["updated"] = False
        return instrument

    # add new virtual_instrument in virtual_instruments
    def __add_new_virtual_instrument(self, current_virtual_instrument):
        if len(self.virtual_instruments) > 0:
            last_element = self.virtual_instruments[-1]
            last_id = last_element["id"]
        else:
            last_id = 0

        new_virtual_instrument = {
            "id": last_id + 1,
            "fk_instrument": current_virtual_instrument["instrument_id"],
            "frequencies": current_virtual_instrument["frequencies"],
            "new_entry": True
        }
        return new_virtual_instrument

    def __add_new_station(self, station_name):
        sql_query = """INSERT INTO stations (station_name) VALUES ('%s') RETURNING id, station_name, ephemeris_start, ephemeris_end, observation_start, observation_end, obs_lon, obs_lat, duration;"""
        database = self.get_db()

        with database.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(sql_query % station_name)
            station = dict(cursor.fetchone())
        database.commit()
        cursor.close()

        station["updated"] = False
        return station

    # child_run() process for multiprocessing.pool
    def __import_directory_fits(self):
        while True:
            # block + dequeue
            fits_file = self.fits_queue.get()

            # exit gracefully
            if fits_file == "END":
                break

            # log current file which is proceeding right now
            file_name = os.path.basename(fits_file)
            print('importing "%s"...' % file_name)
            try:
                observation_times, virtual_instrument_id = self.__gen_import_values(fits_file)
            except Exception:
                ex_str = traceback.format_exc()
                print("Warning: could not import file '%s' since there is an uncaught error: %s" % (file_name, ex_str))
                continue

            # delete all the right side of the image tree
            # it gets the image position (tree index!), for the quicklook!
            if observation_times is not None:
                relative_file_path = "/" + "/".join(fits_file.rsplit("/", 4)[1:])
                observation_times_str = "[%s,%s]" % (
                    observation_times.lower.isoformat(), observation_times.upper.isoformat())
                self.value_strings.append(
                    "%s\t%s\t%s\t%s" % (virtual_instrument_id, datetime.datetime.now().isoformat(),
                                        observation_times_str, relative_file_path))

                if self.delete_related_tiles:
                    if virtual_instrument_id not in self.tile_remove:
                        self.tile_remove[virtual_instrument_id] = [set() for i in
                                                                      range(ecallisto_config.MAX_TILE_LEVEL + 1)]

                    for i in range(ecallisto_config.MAX_TILE_LEVEL + 1):
                        start_i = ecallisto.sources.fits_sampler.datetime_level_to_index(observation_times.lower, i)
                        end_i = ecallisto.sources.fits_sampler.datetime_level_to_index(observation_times.upper, i)
                        self.tile_remove[virtual_instrument_id][i].update(range(start_i, end_i + 1))

    def get_db(self):
        return psycopg2.connect(host=ecallisto_config.DB_HOST,
                                database=ecallisto_config.DB_DATABASE,
                                user=ecallisto_config.DB_USER,
                                password=ecallisto_config.DB_PASSWORD)

    def __get_instruments_and_virtual_instruments(self, database):
        instruments = ecallisto.sources.instruments.get_all_instruments(database, ignore_unknown=False)
        virtual_instruments = ecallisto.sources.instruments.get_all_virtual_instruments(database)

        for i in instruments:
            i["updated"] = False

        for i in virtual_instruments:
            i["new_entry"] = False

        [self.instruments.append(instrument) for instrument in instruments]
        [self.virtual_instruments.append(virtual_instrument) for virtual_instrument in virtual_instruments]

    def __get_stations(self, database):
        stations = ecallisto.sources.stations.get_stations(database)
        for i in stations:
            i["updated"] = False

        [self.stations.append(station) for station in stations]

    def __to_timestamp(self, date_string, time_string):
        # time leaps lead to parse error
        sixty_second_leap = int(time_string[6:8]) == 60
        sixty_minutes_leap = int(time_string[3:5]) == 60
        twenty_four_hours_leap = int(time_string[:2]) == 24

        # replace 60 through 59
        if sixty_second_leap:
            time_string = time_string[:6] + '59' + time_string[8:]

        if sixty_minutes_leap:
            time_string = time_string[:3] + '59' + time_string[5:]

        if twenty_four_hours_leap:
            time_string = '23' + time_string[2:]

        if re.findall("\.\d+", time_string):
            time_string = time_string[:-4]

        ts = None
        for date_format in ['%Y/%m/%d %H:%M:%S', '%d/%m/%y %H:%M:%S']:
            try:
                ts = datetime.datetime.strptime('%s %s' % (date_string, time_string), date_format)
                error = None
                break
            except ValueError as e:
                error = e
                continue

        if error:
            raise error

        # add lost time
        ts += datetime.timedelta(hours=int(twenty_four_hours_leap),
                                 minutes=int(sixty_minutes_leap),
                                 seconds=int(sixty_second_leap))
        return ts

    def __get_unregistered_fits_files(self, data_dir):
        # get all fits files from data_dir

        extensions = ["*.fit", "*.fits", "*.fit.gz", "*.fits.gz"]
        fits_files = set()
        for i in extensions:
            fits_files.update(glob.glob(os.path.join(data_dir, i)))

        if len(fits_files) == 0:
            return

        fits_files = {fits_file.replace(ecallisto_config.DATA_PATH, '') for fits_file in fits_files}

        database = self.get_db()
        cursor = database.cursor()
        sql_select = """SELECT path FROM fits WHERE path IN %s"""

        # get only the fits files, which are not yet imported
        cursor.execute(sql_select, (tuple(fits_files),))
        already_existing = set(map(lambda a: a[0], cursor.fetchall()))

        fits_files = fits_files - already_existing
        fits_files = [ecallisto_config.DATA_PATH + fits_file for fits_file in fits_files]
        return fits_files

    def __find_instrument_by_filename(self, filename):
        for instrument_list_index, instrument in enumerate(self.instruments):
            if re.search(instrument["regex"], filename) is not None:
                return instrument_list_index, instrument
        return None, None

    def __find_station(self, station_name, stations):
        for station_list_index, station in enumerate(stations):
            if station["station_name"] == station_name:
                return station_list_index, station
        return None, None

    # updates only the instrument in the set list, not in DB!
    def __update_instrument(self, instrument_list_index, instrument, fk_station_id, origin, start_data, end_data):
        if instrument["fk_station"] is None:
            d = self.instruments[instrument_list_index]
            d["fk_station"] = fk_station_id
            d["updated"] = True
            self.instruments[instrument_list_index] = d

        if instrument["origin"] is None:
            d = self.instruments[instrument_list_index]
            d["origin"] = origin
            d["updated"] = True
            self.instruments[instrument_list_index] = d

        if (instrument["start_data"] is None and start_data is not None) or start_data < instrument["start_data"]:
            d = self.instruments[instrument_list_index]
            d["start_data"] = start_data
            d["updated"] = True
            self.instruments[instrument_list_index] = d

        if (instrument["end_data"] is None and end_data is not None) or end_data > instrument["end_data"]:
            d = self.instruments[instrument_list_index]
            d["end_data"] = end_data
            d["updated"] = True
            self.instruments[instrument_list_index] = d

    def __update_station(self, station_list_index, station, obs_lat, obs_lon):
        if station["obs_lat"] is None and obs_lat is not None:
            d = self.stations[station_list_index]
            d["obs_lat"] = obs_lat
            d["updated"] = True
            self.stations[station_list_index] = d

        if station["obs_lon"] is None and obs_lon is not None:
            d = self.stations[station_list_index]
            d["obs_lon"] = obs_lon
            d["updated"] = True
            self.stations[station_list_index] = d

    # update meta data of each instrument
    def __update_instruments(self):
        database = self.get_db()
        cursor = database.cursor()
        for instrument in self.instruments:
            if not instrument["updated"]:
                continue
            sql_update_instr = """UPDATE instruments SET fk_station=%s, origin=%s, start_data=%s, end_data=%s WHERE id=%s"""
            cursor.execute(sql_update_instr, (
                instrument["fk_station"],
                instrument["origin"],
                instrument["start_data"],
                instrument["end_data"],
                instrument["id"]
            ))
            instrument["updated"] = False
        database.commit()
        cursor.close()

    # add new virtual instruments in db
    def __add_new_virtual_instruments_in_db(self):
        database = self.get_db()
        cursor = database.cursor()
        for virtual_instrument in self.virtual_instruments:
            if virtual_instrument["new_entry"]:
                sql_insert_instr = """INSERT INTO virtual_instruments (fk_instrument, frequencies) VALUES (%s, %s)"""
                cursor.execute(sql_insert_instr, (
                    virtual_instrument["fk_instrument"],
                    virtual_instrument["frequencies"]
                ))
                virtual_instrument["new_entry"] = False
                continue

        database.commit()
        cursor.close()

    def __find_virtual_instrument(self, virtual_instrument_list, frequencies):
        for virtual_instrument in virtual_instrument_list:
            if virtual_instrument["frequencies"] == frequencies:
                return virtual_instrument
        return None

    def __gen_import_values(self, fits_file):
        # hdulist checks
        hdulist = None
        try:
            hdulist = fits.open(fits_file)
            origin = hdulist[0].header["ORIGIN"]
            station_name = hdulist[0].header["INSTRUME"]
        except Exception:
            print("Warning: Could not import file '%s' since there is an error while reading the file" % fits_file)
            if hdulist is not None:
                hdulist.close()
            return None, None

        # filename checks
        instrument_list_index, instrument = self.__find_instrument_by_filename(fits_file)

        if instrument is None:
            file_name = fits_file.rsplit('/', 1)[1]
            file_name_ending = file_name.split('.', 1)
            file_name = file_name_ending[0]
            _, instrument_name = self.__get_regex_pattern(file_name)
            if instrument_name not in self.missing_instruments:
                self.missing_instruments[instrument_name] = fits_file
            return None, None

        # Either there is no entry in the stations table or there is just no reference yet to the instruments table
        station_list_index, station = self.__find_station(station_name, self.stations)

        if station is None:
            self.missing_stations[station_name] = station_name
            return None, None

        hdu1_data = None
        try:
            if len(hdulist) > 1:
                hdu1_data = hdulist[1].data
        except Exception:
            print(
                "Warning: Could not import file '%s' since there is an error while reading the frequencies from the file" % fits_file)
            hdulist.close()
            return None, None

        if hdu1_data is None:
            try:
                start_freq = hdulist[0].header["CRVAL2"]
            except Exception:
                print(
                    "Warning: Could not import file '%s' since there is an error while reading the CRVAL2 from the file" % fits_file)
                hdulist.close()
                return None, None

            try:
                step_freq = hdulist[0].header["CDELT2"]
            except Exception:
                print(
                    "Warning: Could not import file '%s' since there is an error while reading the CDELT2 from the file" % fits_file)
                hdulist.close()
                return None, None

            try:
                frequencies = list(reversed(list(numpy.arange(start_freq, 0, step_freq, numpy.float64))))
            except Exception:
                print(
                    "Warning: Could not import file '%s' since there is an error while trying calculating the frequencies from the file" % fits_file)
                hdulist.close()
                return None, None
        else:

            try:
                frequencies = list(reversed(hdulist[1].data.field('FREQUENCY')[0].tolist()))
            except Exception:
                print(
                    "Warning: Could not import file '%s' since there is an error while trying reading the frequencies from the file" % fits_file)
                hdulist.close()
                return None, None

        try:
            # some fits files do not have a dimension, that's why height is not used!
            height = hdulist[0].data.shape[0]
        except Exception:
            print(
                "Warning: Could not import file '%s' since there is an error while reading the data from the file" % fits_file)
            hdulist.close()
            return None, None

        if len(frequencies) != hdulist[0].data.shape[0]:
            print(
                "Warning: Given number of frequencies(%d) in file to not match height of data(%d), ignore file %s" % (
                    len(frequencies), hdulist[0].data.shape[0], fits_file
                )
            )
            return None, None

        # convert time
        try:
            date_obs = hdulist[0].header['DATE-OBS']
        except Exception:
            print(
                "Warning: Could not import file '%s' since there is an error while reading the DATE-OBS from the file" % fits_file)
            hdulist.close()
            return None, None

        try:
            time_obs = hdulist[0].header['TIME-OBS']
        except Exception:
            print(
                "Warning: Could not import file '%s' since there is an error while reading the TIME-OBS from the file" % fits_file)
            hdulist.close()
            return None, None

        try:
            date_end = hdulist[0].header['DATE-END']
        except Exception:
            print(
                "Warning: Could not import file '%s' since there is an error while reading the DATE-END from the file" % fits_file)
            hdulist.close()
            return None, None

        try:
            time_end = hdulist[0].header['TIME-END']
        except Exception:
            print(
                "Warning: Could not import file '%s' since there is an error while reading the TIME-END from the file" % fits_file)
            hdulist.close()
            return None, None

        try:
            obs_lat = hdulist[0].header['OBS_LAT']
        except Exception:
            print(
                "Warning: Could not import file '%s' since there is an error while reading the OBS_LAT from the file" % fits_file)
            hdulist.close()
            return None, None

        try:
            obs_lon = hdulist[0].header['OBS_LON']
        except Exception:
            print(
                "Warning: Could not import file '%s' since there is an error while reading the OBS_LON from the file" % fits_file)
            hdulist.close()
            return None, None

        hdulist.close()

        start_obs_timestamp = self.__to_timestamp(date_obs, time_obs)
        end_obs_timestamp = self.__to_timestamp(date_end, time_end)

        # update each instrument by its new value
        self.__update_instrument(instrument_list_index, instrument, station["id"], origin, start_obs_timestamp,
                                 end_obs_timestamp)
        self.__update_station(station_list_index, station, obs_lat, obs_lon)

        database = self.get_db()
        virtual_instrument = ecallisto.sources.instruments.get_virtual_instrument(database, instrument["id"], frequencies)

        if virtual_instrument is None:
            new_virtual_instrument = {"instrument_id": instrument["id"], "frequencies": frequencies}
            self.missing_virtual_instruments[station_name] = new_virtual_instrument
            return None, None

        observation_times = psycopg2.extras.DateTimeRange(start_obs_timestamp, end_obs_timestamp, "[]")

        return observation_times, virtual_instrument["id"]