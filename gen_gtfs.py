import datetime
import os
import pandas as pd
from pyproj import Proj, transform
import re
import zipfile
import click

@click.command()
@click.option('--indir', default='pkl', help='Input Directory')
@click.option('--outdir', default='gtfs', help='Output Directory')
def gen_gtfs(indir, outdir):
    """
    Convert the pickle files into the gtfs file zip format for various purposes
    """
    db_name_list = [
        'COMPANY_CODE',
        'ROUTE_BUS',
        'RSTOP_BUS',
        'STOP_BUS',
        'FARE_BUS',
        ]
    if not os.path.exists(outdir):
        os.makedirs(outdir)    

    # Import all data files
    df_dict = {}
    for db_name in db_name_list:
        df_dict[db_name] = pd.read_pickle(indir + '/' + db_name + '.pkl')

    print(df_dict.keys())        

    # Coordinate Transform
    WGS84 = Proj(init='EPSG:4326')
    HK80 = Proj(init='EPSG:2326')
    
    # from company_code to agency.txt
    print('Generating agency.txt')
    with open(outdir + '/' + 'agency.txt', 'w') as f:
        f.write('agency_id,agency_name,agency_url,agency_timezone\n')
        for i,c in df_dict['COMPANY_CODE'].iterrows():
            f.write('%s,%s,http://www.xxx.com,Asia/Shanghai\n' % (c.COMPANY_CODE, c.COMPANY_NAMEE))
            
    # from rstop_bus to routes.txt
    route_id_ary = []
    print('Generating routes.txt')
    with open(outdir + '/' + 'routes.txt', 'w') as f:
        f.write('route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color\n')                
        for i,r in df_dict['ROUTE_BUS'].iterrows():
            route_id_ary.append(r.ROUTE_ID)
            f.write('%d,%s,,%s,,3,%s,,\n' % (r.ROUTE_ID, r.COMPANY_CODE, r.ROUTE_NAMEE, r.HYPERLINK_E))
            
    # from rstop_bus to trips.txt
    print('Generating trips.txt')
    with open(outdir + '/' + 'trips.txt', 'w') as f:
        f.write('route_id,service_id,trip_id,trip_headsign,direction_id,block_id,shape_id\n')        
        for i,r in df_dict['ROUTE_BUS'].iterrows():
            for direction in range(2):
                trip_id = '%d_%d' % (r.ROUTE_ID, direction)
                f.write('%d,%s,%s,,%d,,\n' % (r.ROUTE_ID, 'FULLW', trip_id, direction))

    # from stop_bus to stops.txt
    print('Generating stops.txt')
    with open(outdir + '/' + 'stops.txt', 'w') as f:
        f.write('stop_id,stop_name,stop_desc,stop_lat,stop_lon,zone_id,stop_url\n')
        stop_count = 0
        unique_stop_df = df_dict['RSTOP_BUS'].drop_duplicates('STOP_ID')
        for i,rstop in unique_stop_df.iterrows():
            stop_id = rstop.STOP_ID
            stop_namee = rstop.STOP_NAMEE
            stop_namee = stop_namee.replace(',', ' ')
            stop_namee = re.sub(r'[^\x00-\x7f]',r' ',stop_namee)
            
            stop_df = df_dict['STOP_BUS']
            stop = stop_df.loc[stop_df.STOP_ID == stop_id]
            x, y = transform(HK80, WGS84, float(stop.X), float(stop.Y))
            f.write('%d,"%s",,%f,%f,%d,\n' % (stop_id, stop_namee, y, x, stop_count / 3))
            stop_count += 1           

    # from stop_bus to stop_times.txt
    print('Generating stop_times.txt')    
    with open(outdir + '/' + 'stop_times.txt', 'w') as f:
        f.write('trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign,pickup_type,drop_off_type,shape_dist_traveled\n')
        start_time = datetime.datetime(2018,1,1,5,30,0)
        for route_id in route_id_ary:
            for direction in range(2):
                trip_id = '%d_%d' % (route_id, direction)
                stop_count = 0        
                rstop_df = df_dict['RSTOP_BUS']
                rstop_data = rstop_df.loc[(rstop_df.ROUTE_ID == route_id) & (rstop_df.ROUTE_SEQ == direction+1)]
                rstop_data = rstop_data.sort_values('STOP_SEQ')
                for i,rstop in rstop_data.iterrows():
                    offset = datetime.timedelta(minutes=5*stop_count)
                    arr_time = (start_time + offset).strftime('%H:%M:%S')
                    offset = datetime.timedelta(minutes=5*stop_count+1)
                    dep_time = (start_time + offset).strftime('%H:%M:%S')
                    f.write('%s,%s,%s,%d,%d,,,,\n' % (trip_id,arr_time,dep_time,rstop.STOP_ID,rstop.STOP_SEQ))
                    stop_count += 1

    # calendar.txt
    print('Generating calendar.txt')      
    with open(outdir + '/' + 'calendar.txt', 'w') as f:
        f.write('service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n')
        f.write('FULLW,1,1,1,1,1,1,1,20180101,20181231\n')

    # calendar_dates.txt
    print('Generating calendar_dates.txt')   
    with open(outdir + '/' + 'calendar_dates.txt', 'w') as f:
        f.write('service_id,date,exception_type\n')
        f.write('FULLW,20070604,2\n')
    
    # from fare_bus to fare_attributes.txt
    fare_list = []
    print('Generating fare_attributes.txt') 
    with open(outdir + '/' + 'fare_attributes.txt', 'w') as f:
        f.write('fare_id,price,currency_type,payment_method,transfers,transfer_duration\n')
        unique_fare_df = df_dict['FARE_BUS'].drop_duplicates('PRICE')
        unique_fare_df = unique_fare_df.sort_values('PRICE')
        unique_fare_df = unique_fare_df.reset_index()        
        for i,d in unique_fare_df.iterrows():
            f.write('%d,%f,HKD,0,0,\n'  % (i, d.PRICE))
            fare_list.append(d.PRICE)

    # from fare_bus to fare_rules.txt
    print('Generating fare_rules.txt') 
    with open(outdir + '/' + 'fare_rules.txt', 'w') as f:
        f.write('fare_id,route_id,origin_id,destination_id,contains_id\n')        
        fare_df = df_dict['FARE_BUS'].sort_values('ROUTE_ID')        
        for i,d in fare_df.iterrows():
            fare_id = fare_list.index(d.PRICE)
            f.write('%d,%s,%d,%d,\n'  % (fare_id, d.ROUTE_ID, d.ON_SEQ, d.OFF_SEQ))            

    # Zip to output file
    with zipfile.ZipFile('gtfs-hk.zip', mode='w') as zf:
        for f in os.listdir(outdir):
            zf.write(outdir + '/' + f, f)            

    return df_dict
    
if __name__ == "__main__":
    df_dict = generate_gtfs('pkl', 'gtfs')
