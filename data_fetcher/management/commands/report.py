# data_fetcher/management/commands/report.py

from django.core.management.base import BaseCommand, CommandError
import requests
import json, os
from datetime import datetime,date, timedelta
import pandas as pd
from io import StringIO
from data_fetcher.models import Install_Data
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
    help = 'Reporting.'
    
    def handle(self, *args, **options):
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
                print(f"Ngày: {date}, AppID: {app}, App: {get_name_by_appid(app)} Số lượng bản ghi: {count}")


        