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
    help = 'Reporting.'
    
    def handle(self, *args, **options):
        qs = Install_Data.objects.filter(
            app_id='id6742221896',  # dreamy
            install_date=date.today() - timedelta(days=1),
        
        ).order_by('-id').values()[:3]  # Lấy 3 dòng đầu tiên

        for row in qs:
            print(row)

        

        
  
        
        