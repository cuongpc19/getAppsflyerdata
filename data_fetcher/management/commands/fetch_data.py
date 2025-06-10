# data_fetcher/management/commands/fetch_data.py

from django.core.management.base import BaseCommand, CommandError
import requests
import json
from datetime import datetime,date, timedelta
import pandas as pd
from io import StringIO
from data_fetcher.models import Install_Data
from django.utils import timezone
from .api_keys import API_TOKEN

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
                    if report_type == 'organic_installs_report':
                        campaign = 'Organic'
                        media_source = 'Organic'
                    else:
                        campaign = item['Campaign']
                        media_source = item['Media Source']
                    #install_data_list.append(item['AppsFlyer ID'] + ',' + campaign+ ','  + media_source + ',' + item['Install Time']+ ',' + item['Platform']+ ',' + item['City']+ ',' + item['Country Code']+ ',' + item['Device Model'])
                    # Save to DB
                    dt_naive = datetime.strptime(item['Install Time'], "%Y-%m-%d %H:%M:%S")
                    install_time_aware = timezone.make_aware(dt_naive)
                    if not Install_Data.objects.filter(appsflyer_id=item['AppsFlyer ID']).exists():
                        Install_Data.objects.create(
                            appsflyer_id=item['AppsFlyer ID'],
                            campaign_name=campaign,
                            media_source=media_source,
                            install_time=install_time_aware,
                            install_date=dt_naive.date(),
                            platform=item['Platform'],
                            city=item['City'],
                            country=item['Country Code'],
                            device=item['Device Model'],
                        )
            
            filelocation = f'data_fetcher/management/commands/{app_id}_AID_{report_type}.txt'
            array_to_file(install_data_list, filelocation)
    except requests.exceptions.RequestException as e:
        raise CommandError(f'Error fetching from API: {e}')
    except json.JSONDecodeError:
        raise CommandError('Error decoding JSON response from API.')

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

class Command(BaseCommand):
    help = 'Fetches data from an external API and processes it.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting data fetching process...'))
        
        FROM_DATE = '2025-06-03'
        TO_DATE = '2025-06-05'
    
        app_id_lst = [
        {
            'app_id': 'id6742221896',
            'platform': 'ios'
        },
        {
            'app_id': 'com.abi.dream.unpacking',
            'platform': 'android'
        }
    ]
        report_type = ['organic_installs_report','installs_report']
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
        ten_days_ago = timezone.now().date() - timedelta(days=10)
        Install_Data.objects.filter(install_date__lt=ten_days_ago).delete()
        for report_t in report_type:
            for app in app_id_lst:
                app_id = app['app_id']
                api_url = 'https://hq1.appsflyer.com/api/raw-data/export/app/{}/{}/v5'.format(app_id, report_t)
                try:
                    
                    # Gọi hàm riêng biệt để lấy dữ liệu
                    fetched_data = _perform_data_fetch(api_url, params_appsflyer, headers,app_id,report_t)
                    self.stdout.write(self.style.SUCCESS('Data fetched successfully.'))
                    #self.stdout.write(json.dumps(fetched_data, indent=2))

                    # Gọi hàm riêng biệt để lưu dữ liệu (nếu có)
                    #_save_data_to_db(fetched_data)
                    self.stdout.write(self.style.SUCCESS('Data successfully saved (simulated).'))

                except CommandError as e:
                    self.stdout.write(self.style.ERROR(str(e)))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {e}'))

        self.stdout.write(self.style.NOTICE('Data fetching process finished.'))