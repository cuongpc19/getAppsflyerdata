# data_fetcher/management/commands/fetch_data.py

from django.core.management.base import BaseCommand, CommandError
import requests
import json, os
from datetime import datetime,date, timedelta
import pandas as pd
from io import StringIO
from data_fetcher.models import Install_Data,Request_Data
from django.utils import timezone
from .api_keys import API_TOKEN
import logging
import sys
sys.path.insert(0, '/home/mkt-en/wood_nood_data')
logger = logging.getLogger('data_fetcher')
from ...constants import app_id_lst

        
# Hàm riêng biệt chứa logic lấy dữ liệu chính
def _perform_data_fetch(api_url, params, headers,app_id,report_type):
    """
    Handles the actual data fetching logic.
    Returns the fetched data or raises an exception.
    """
    install_data_list = []
    try:
        res_appsflyer = requests.request('GET', api_url, params=params, headers=headers)
        if res_appsflyer.status_code != 200:
                raise CommandError('Error decoding JSON response from API.')
        else:
            install_data_list.append('AppsFlyer ID,Campaign,Media Source,Install Time,Platform,City,Country Code,Device Model')
            # Define the batch size
            batch_size = 1000
            # Read the CSV file in chunks
            columns_to_keep = ['AppsFlyer ID','Ad ID', 'Campaign ID','Advertising ID','Campaign','Media Source', 'Install Time', 'Platform', 'City', 'Country Code', 'Device Model']
            
            for chunk in pd.read_csv(StringIO(res_appsflyer.text), usecols=columns_to_keep, chunksize=batch_size, keep_default_na=False):
                chunk.replace('', None, inplace=True)
                for _, item in chunk.iterrows():
                    if report_type == 'reinstalls_organic':
                        campaign = 'Organic'
                        media_source = 'Organic'
                    else:
                        campaign = item['Campaign']
                        media_source = item['Media Source']
                    #install_data_list.append(item['AppsFlyer ID'] + ',' + campaign+ ','  + media_source + ',' + item['Install Time']+ ',' + item['Platform']+ ',' + item['City']+ ',' + item['Country Code']+ ',' + item['Device Model'])
                    # Save to DB
                    dt_naive = datetime.strptime(item['Install Time'], "%Y-%m-%d %H:%M:%S")
                    install_time_aware = timezone.make_aware(dt_naive)
                    if not Install_Data.objects.filter(app_id=app_id,appsflyer_id=item['AppsFlyer ID']).exists():
                        Install_Data.objects.create(
                            appsflyer_id=item['AppsFlyer ID'],
                            app_id=app_id,
                            campaign_name=campaign,
                            media_source=media_source,
                            install_time=install_time_aware,
                            install_date=dt_naive.date(),
                            platform=item['Platform'],
                            city=item['City'],
                            country=item['Country Code'],
                            device=item['Device Model'],
                            inserted_time=timezone.now(),
                            reporttype =  report_type,
                        )
            
            #filelocation = f'data_fetcher/management/commands/{app_id}_AID_{report_type}.txt'
            #array_to_file(install_data_list, filelocation)
    except requests.exceptions.RequestException as e:
        raise CommandError(f'Error fetching from API: {e}')
        logger.error(f'Error fetching data from API for app_id: {app_id} with report type: {report_type} - {e}')
    except json.JSONDecodeError:
        raise CommandError('Error decoding JSON response from API.')
        logger.error(f'Error fetching JSON from API for app_id: {app_id} with report type: {report_type} - {e}')

# Hàm riêng biệt để lưu dữ liệu vào DB (ví dụ)
def _save_data_to_db(data):
    """
    Handles saving the fetched data to the database.
    """
    # Thay thế bằng logic lưu DB thực tế của bạn
    print(f"Simulating saving data to DB: {len(data.keys())} items")
    # Ví dụ: from data_fetcher.models import MyDataModel
    # MyDataModel.objects.create(some_field=data.get('some_key'))
    # ...
    pass

def array_to_file(array, file_path):
    """
    Saves an array to a file, one item per line.
    """
    with open(file_path, 'w') as file:
        for item in array:
            file.write(f"{item}\n")
    print(f"Data saved to {file_path}")

def get_name_by_appid(appid):
    for app in app_id_lst:
        if app['app_id'] == appid:
            return app['name']
    return None

class Command(BaseCommand):
    help = 'Fetches data from an external API and processes it.'
    
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting data fetching process...'))
        
        start = timezone.now().date() - timedelta(days=18)
        end = timezone.now().date() - timedelta(days=13)
    
        FROM_DATE = start.strftime("%Y-%m-%d")
        TO_DATE = end.strftime("%Y-%m-%d")
        logger.info('Starting data fetching process:' + FROM_DATE + ' to ' + TO_DATE)

        report_type = ['reinstalls_organic','reinstalls']
        params_appsflyer = {
            'from': FROM_DATE,
            'to': TO_DATE,
            'maximum_rows': 1000000,
            'additional_fields': ['device_model'], 
        }
        headers = {
            "accept": "text/csv",
            "authorization": ("Bearer " + str(API_TOKEN)).replace("\'","")
        }
        #xoa du lieu cu
        seven_days_ago = timezone.now().date() - timedelta(days=27)
        Install_Data.objects.filter(install_date__lt=seven_days_ago).delete()
        for report_t in report_type:
            for app in app_id_lst:
                app_id = app['app_id']
                logger.info(f'Starting data fetch for app_id: {app_id} with report type: {report_t}')
                api_url = 'https://hq1.appsflyer.com/api/raw-data/export/app/{}/{}/v5'.format(app_id, report_t)
                try:
                    
                    # Gọi hàm riêng biệt để lấy dữ liệu
                    fetched_data = _perform_data_fetch(api_url, params_appsflyer, headers,app_id,report_t)
                    self.stdout.write(self.style.SUCCESS('Data fetched successfully.'))
                    logger.info(f'Data fetched successfully for app_id: {app_id} with report type: {report_t}')

                except CommandError as e:
                    self.stdout.write(self.style.ERROR(str(e)))
                    logger.info(f'Error fetching data for app_id: {app_id} with report type: {report_t} - {str(e)}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
                    logger.info(f'An unexpected error occurred for app_id: {app_id} with report type: {report_t} - {str(e)}')
                
        self.stdout.write(self.style.NOTICE('Data fetching process finished.'))

        distinct_date = Install_Data.objects.values_list('install_date', flat=True).distinct()
        list_date = list(distinct_date)

        distinct_app = Install_Data.objects.values_list('app_id', flat=True).distinct()
        # distinct_categories là một QuerySet. Để xem nó như một list Python:
        list_app = list(distinct_app)
        for app in list_app:
           for date in list_date:
                # Lấy các bản ghi cho ngày và nền tảng cụ thể
                records = Install_Data.objects.filter(install_date=date, app_id=app)
                count = records.count()
                logger.info(f"Ngày: {date}, AppID: {app}, App: {get_name_by_appid(app)} Số lượng bản ghi: {count}")

        for app in list_app:
           for date in list_date:
               
                # Moi ngay co bao nhieu request co appsflyerID duoc tra ve
                records = Install_Data.objects.filter(install_date=date, app_id=app, is_get_data=True)
                count = records.count()
                logger.info(f"So luong request valid - Ngày: {date}, AppID: {app}, App: {get_name_by_appid(app)} Số lượng bản ghi: {count}")

        for app in list_app:
            # Request gui len
            records = Request_Data.objects.filter(inserted_time__date=timezone.now().date(), app_id=app)
            count = records.values('appsflyer_id').distinct().count()
            logger.info(f"All request  - Ngày: {timezone.now().date()}, AppID: {app}, App: {get_name_by_appid(app)} Số lượng bản ghi : {count}")

        for app in list_app:
            # Report reinstall
            for date in list_date:
                records = Install_Data.objects.filter(install_date=date, app_id=app, reporttype='reinstalls')
                count = records.values('appsflyer_id').distinct().count()
                logger.info(f"Reinstall - Ngày: {timezone.now().date()}, AppID: {app}, App: {get_name_by_appid(app)} Số lượng bản ghi reinstall : {count}")

                records = Install_Data.objects.filter(install_date=date, app_id=app, reporttype='reinstalls_organic')
                count = records.values('appsflyer_id').distinct().count()
                logger.info(f"Reinstall - Ngày: {timezone.now().date()}, AppID: {app}, App: {get_name_by_appid(app)} Số lượng bản ghi reinstalls_organic : {count}")
