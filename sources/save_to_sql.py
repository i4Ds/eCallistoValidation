#from packages.modules import *
#from packages.main import *
from validation import *

def __to_timestamp(date_string, time_string):
    sixty_seconds = int(time_string[6:8]) == 60
    sixty_minutes = int(time_string[3:5]) == 60
    twentyfour_hours = int(time_string[:2]) == 24

    # replacing  24 to 00
    if sixty_seconds:
        time_string = time_string[:6] + '59' + time_string[8:]
    if sixty_minutes:
        time_string = time_string[:3] + '59' + time_string[5:]
    if twentyfour_hours:
        time_string = '23' + time_string[2:]
    if re.findall('\.\d+ ', time_string):
        time_string = time_string[:-4]

    # lost time
    ts = datetime.datetime.strptime(
        '%s %s' % (date_string, time_string), '%Y/%m/%d %H:%M:%S')
    ts += datetime.timedelta(hours=int(twentyfour_hours),
                             minutes=int(sixty_minutes),
                             seconds=int(sixty_seconds))

    return ts


path = '/data/radio//2002-20yy_Callisto//2017/09//01'

engine = create_engine("postgresql+psycopg2://" + 'postgres' + ":" + 'ecallistohackorange' + "@" + 'localhost' + "/" + 'validation')


def save_metaData():
    df = 0

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith('.fit.gz'):
                full_path = os.path.join(root, name)

                hdulist = astropy.io.fits.open(full_path)
                split_path = full_path.split("Callisto/")

                instrument_name = hdulist[0].header['INSTRUME']
                date_obs = hdulist[0].header['DATE-OBS']
                time_obs = hdulist[0].header['TIME-OBS']
                date_end = hdulist[0].header['DATE-END']
                time_end = hdulist[0].header['TIME-END']

                # combine date and time obs, date and time end
                start_time = __to_timestamp(date_obs, time_obs)
                end_time = __to_timestamp(date_end, time_end)

                # creating dataframe in pandas

                data = {
                    'path': [split_path[1]],
                    'file_name': [name],
                    'instrument_name': [instrument_name],
                    'start_time': [start_time],
                    'end_time': [end_time],
                    'std': [None]
                }

                data_frame = pd.DataFrame(data, index=[df])

                # connection between pandas and sql
                data_frame.to_sql('data', con=engine,
                                  if_exists='append', chunksize=10000000, index=False)

                df = df + 1


save_metaData()
