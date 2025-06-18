# data_fetcher/management/commands/report.py

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
logger = logging.getLogger('data_fetcher')
from ...constants import app_id_lst

def get_app_id_by_platform_and_name(platform, name):
    """
    Tìm và trả về app_id từ APP_INFO_LIST dựa trên platform và tên game.
    Trả về None nếu không tìm thấy.
    """
    for app in app_id_lst:
        if app['platform'] == platform and app['name'] == name:
            return app['app_id']
    return None

def get_name_by_appid(appid):
    """
    Tìm và trả về app_id từ APP_INFO_LIST dựa trên platform và tên game.
    Trả về None nếu không tìm thấy.
    """
    for app in app_id_lst:
        if app['app_id'] == appid:
            return app['name']
    return None

class Command(BaseCommand):
    help = 'Checking.'
    def add_arguments(self, parser):
        parser.add_argument('appsflyerID', type=str, help='appsflyerID of the user to check')
    
    def handle(self, *args, **options):
        appsflyerID = options['appsflyerID']
        #check install data
        install_data = Install_Data.objects.filter(appsflyer_id=appsflyerID).first()
        #install_data = Install_Data.objects.filter(install_date=(timezone.now().date() - timedelta(days=2)) , platform = 'android', app_id = 'com.abi.dream.unpacking').first()
        if install_data:
            print(f"Install data for appsflyerID {appsflyerID} found.")
            for field in Install_Data._meta.fields:
                field_value = getattr(install_data, field.name)
                if field_value is not None:
                    print(self.style.SUCCESS(f"{field.name}: {field_value}"))
        else:
            print(f"No install data found for appsflyerID {appsflyerID}.")
        
        #check request data
        request_data = Request_Data.objects.filter(appsflyer_id=appsflyerID).first()
        if request_data:
            print(f"Request data for appsflyerID {appsflyerID} found.")
            for field in Request_Data._meta.fields:
                field_value = getattr(request_data, field.name)
                if field_value is not None:
                    print(self.style.SUCCESS(f"{field.name}: {field_value}"))
        else:
            print(f"No request data found for appsflyerID {appsflyerID}.")
        