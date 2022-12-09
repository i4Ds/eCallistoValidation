from validation import *


def _to_stars(spec, percentage: int, ranges=None, decimal=None):
    spec_constbacksub = spec.subtract_bg( "subtract_bg_sliding_window", window_width=5, affected_width=1 )
    data = np.absolute( spec_constbacksub.data.data )
    std = round( np.nanstd( data ), 3 )
    snr = round( np.nanmean( data ) / std, 3 )
"""
    if ranges is None:
        ranges = [(0, 4), (5, 20), (20, 40), (40, 60), (60, 80), (80, 101)]
    for index, ran in enumerate( ranges ):
        if ran[0] <= percentage < ran[1]:^'
            if decimal and percentage >= sum( ran ) // 2:
                return min( index + 0.5, len( ranges ) - 1 )
            return f"{spec.header['INSTRUME']}: {index * '*'}"
    return -1
"""

# spec = CallistoSpectrogram.read( "./GREENLAND_20170906_115501_63.fit" )


sql_query_1 = "select station_name, duration  from stations where duration is not null order by duration desc"

database = get_db()

data_b = get_all_instruments(database,sql_query_1 )

df = pd.DataFrame(data_b)

df_split = np.array_split(df, 5)

while True:
    station_name  =input( "Enter the station name: " )

    if station_name in str(df_split[0][0]):
        print( f"This station {station_name}:  got {5* '*' }" )


    if station_name in str(df_split[1][0]):
        print(f"This station {station_name}:  got {4* '*' }" )


    if station_name in str(df_split[2][0]):
        print( f"This station {station_name}:  got {3* '*' }" )

    if station_name in str(df_split[3][0]):
        print(f"This station {station_name}:  got {2* '*' }" )


    if station_name in str(df_split[4][0]):
        print( f"This station {station_name}: got {1* '*' }" )






