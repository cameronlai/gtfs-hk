import click
import os
import pandas as pd
import pyodbc

@click.command()
@click.option('--indir', default='mdb', help='Input Directory')
@click.option('--outdir', default='pkl', help='Output Directory')
def process_mdb(indir, outdir):
    """
    Convert the mdb files into pickle files that are in the pandas data frame format
    """
    db_name_list = [
        'COMPANY_CODE',
        'ROUTE_BUS',
        'RSTOP_BUS',
        'STOP_BUS',
        'FARE_BUS',
        ]    
    conn_str_prefix = 'Driver={Microsoft Access Driver (*.mdb)};DBQ='

    if not os.path.exists(outdir):
        os.makedirs(outdir)    

    for db_name in db_name_list:
        print('Processing %s' % db_name)
        conn_str = conn_str_prefix + indir + '/' + db_name + '.mdb'
        print(conn_str)
        with pyodbc.connect(conn_str) as conn:
            cur = conn.cursor()
            # TODO: Find a more generic pattern or use a look up table
            table_name = db_name.replace('_BUS', '') # Remove based on bus table rules
            cur.execute(r'SELECT * FROM %s' % table_name)
            columns = [column[0] for column in cur.description]    
            fetch_data = cur.fetchall()
            data = [list(d) for d in fetch_data]
            # Save to output dir
            df = pd.DataFrame(data, columns = columns)
            df.to_pickle(outdir + '/' + db_name + '.pkl')
            
if __name__ == "__main__":
    process_mdb('mdb', 'pkl')
