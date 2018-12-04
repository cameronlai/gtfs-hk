import click
import os
import requests

@click.command()
@click.option('--directory', default='mdb', help='Download Directory')
def download_mdb(directory):
    """
    Download mdb files from the data.gov.hk website
    """
    db_name_list = [
        'COMPANY_CODE',
        'ROUTE_BUS',
        'RSTOP_BUS',
        'STOP_BUS',
        'FARE_BUS',
        ]
    download_url = 'http://static.data.gov.hk/td/routes-and-fares/'  

    if not os.path.exists(directory):
        os.makedirs(directory)

    for db_name in db_name_list:
        print('Downloading %s.' % db_name)
        full_url = download_url + db_name + '.mdb'
        print(full_url)
        resp = requests.get(full_url)
        if resp.status_code == 200:
            print('Successfully downloaded %s.' % db_name)
            with open(directory + '/' + db_name, 'wb') as f:
                f.write(resp.content)        
        else:
            print('Fail to download %s. Status code is %d.' % (db_name, resp.status_code))        
            break

@click.command()
@click.option('--directory', default='pkl', help='Download Directory')
def download_pkl(directory):
    """
    Download pickle files from the github to skip the step of handling mdb files
    """
    print('To be done. You may download directly from github and put it in the pkl folder.')

if __name__ == "__main__":
    download_mdb('mdb')

