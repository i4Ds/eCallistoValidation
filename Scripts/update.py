from packages.modules import *
from packages.main import *


def update_all_values():
    """
    Calculate the std and snr, then update them into the table in Database.
    Returns
    -------
    None
    """

    database = psycopg2.connect(host=test_config.DB_HOST,
                                user=test_config.DB_USER,
                                database=test_config.DB_DATABASE,
                                port=test_config.DB_PORT,
                                password=test_config.DB_PASSWORD)

    rows, cursor = get_all_instruments(database)
    for row in rows:
        try:
            spec = CallistoSpectrogram.read(test_config.DATA_PATH + row[1])

            spec2 = spec.subtract_bg("subtract_bg_sliding_window", window_width=800, affected_width=1,
                                     amount=0.05, change_points=True)

            data = np.absolute(spec2.data.flatten())
            std_data = standard_deviation(data)
            snr_data = signal_to_noise(data)

            sql_update_query = f"""UPDATE data SET std = {std_data}, snr= {snr_data} where id = {row[0]} """
            cursor.execute(sql_update_query)
            database.commit()

        except Exception as err:
            print("The Error message is: %s and the file name is %s" % (err, row[2]))

        print("Update Done!")

