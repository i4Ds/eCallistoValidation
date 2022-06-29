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


#sql_query_1 = "select station_name, duration  from stations where duration is not null order by duration desc"
sql_query = "Select stations.station_name,avg(fits.std) as std_avg, avg(fits.snr) as snr_avg, stations.duration From stations left join instruments on stations.id= instruments.fk_station left join virtual_instruments on stations.id = virtual_instruments.fk_instrument left join fits on stations.id  = fits.fk_virtual_instrument where snr is not null Group by stations.station_name, stations.duration order by snr_avg desc ;"
database = get_db()

data_b = get_all_instruments(database,sql_query )

data_df = pd.DataFrame(data_b)

print(data_df)
#data = np.array_split(data_df, 5)
#print(data)
"""
while True:
    station_name  =input( "Enter the station name: " ).upper()

    if station_name in str(data[0][0]):
        print( f"This station {station_name}:  got {5* '*' }" )


    if station_name in str(data[1][0]):
        print(f"This station {station_name}:  got {4* '*' }" )


    if station_name in str(data[2][0]):
        print( f"This station {station_name}:  got {3* '*' }" )

    if station_name in str(data[3][0]):
        print(f"This station {station_name}:  got {2* '*' }" )


    if station_name in str(data[4][0]):
        print( f"This station {station_name}: got {1* '*' }" )

    if station_name not in str(data):
        print("This station doesn't exist")


"""
