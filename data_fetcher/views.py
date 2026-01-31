# myapp/views.py
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Install_Data, Install_DataPush, Request_Data
from .serializers import DataInstallSerializer # <-- Import serializer mới
from .constants import app_id_lst
from django.utils import timezone
import logging
logger = logging.getLogger('appsflyer_push')

class GetCampaignByAppsflyerIDAPIView(APIView):
    """
    API View để chỉ trả về trường 'campaign' dựa trên appsflyerID.
    """
    def get(self, request, appsflyer_id, app_name=None, platform_id=None):
        if app_name is None or platform_id is None:
            allowed_app_ids = ['id6742221896', 'com.abi.dream.unpacking'] #default la dreamy

            obj = Install_Data.objects.filter(
                app_id__in=allowed_app_ids,  # app_id thuộc danh sách này
                appsflyer_id=appsflyer_id    # Và appflyerID phải khớp
            ).first()
        else:
            # Lấy app_id từ danh sách app_id_lst dựa trên platform_id và app_id
            app_info = next((app for app in app_id_lst if app['name'] == app_name and app['platform'] == platform_id), None)
            if not app_info:
                return Response(
                    {"error": "Không tìm thấy ứng dụng với app_name và platform đã cho."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            obj = Install_Data.objects.filter(
                app_id=app_info['app_id'],  # Sử dụng app_id từ danh sách
                appsflyer_id=appsflyer_id    # Và appflyerID phải khớp
            ).first()
            
            #luu thong tin request
            obj_request = Request_Data.objects.filter(
                app_id=app_info['app_id'],  # Sử dụng app_id từ danh sách
                appsflyer_id=appsflyer_id    # Và appflyerID phải khớp
            ).first()
            if not obj_request:
                obj_request = Request_Data.objects.create(
                    appsflyer_id=appsflyer_id,
                    app_id=app_info['app_id'],
                    inserted_time=timezone.now(),
                    #platform=platform_id,
                    platform=platform_id,
                    is_get_data=0,
                )
            else:
                obj_request.number_request += 1
                obj_request.inserted_time=timezone.now()
                obj_request.save()

        if not obj:
            return Response(
                {"error": "Không tìm thấy dữ liệu cho appsflyerID này."},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            obj.is_get_data = True
            obj.save()
            obj_request.is_get_data = True
            obj_request.save()
        # 2. Chuyển đổi đối tượng bằng DataInstallSerializer
        serializer = DataInstallSerializer(obj)

        # 3. Trả về Response cho client
        # serializer.data sẽ chỉ chứa {'campaign': 'Giá trị của campaign'}
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetDataPullByAppsflyerView(APIView):
    def post(self, request):
        data = request.data
        # Xử lý dữ liệu nhận từ Appsflyer ở đây
        
        appsflyer_id = data.get('appsflyer_id')
        app_id = data.get('app_id')
        campaign = data.get('campaign')
        if campaign is None:
            campaign = data.get('media_source')
        #logger.info(f"Appsflyer PUSH DATA appsflyer_id: {data.get('appsflyer_id')}, app_id: {app_id}, campaign: {campaign}, media_source: {data.get('media_source')}, install_time: {data.get('install_time')}, platform: {data.get('platform')}, city: {data.get('city')}, country: {data.get('country')}, device: {data.get('device')}, event_name: {data.get('event_name')}")
        if not appsflyer_id or not app_id:
            return Response({"error": "Missing appsflyer_id or app_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dt_naive = datetime.strptime(data.get('install_time'), "%Y-%m-%d %H:%M:%S")
            install_time_aware = timezone.make_aware(dt_naive)
            install_date_aware = dt_naive.date()
        except (TypeError, ValueError):
            # Nếu lỗi, lấy thời gian hiện tại làm mặc định
            install_time_aware = timezone.now()
            install_date_aware = timezone.now().date()
            
        #logger.info(f"Data saved successfully with install_time_aware: {install_time_aware}, install_date_aware: {install_date_aware}")

        if not Install_DataPush.objects.filter(app_id=app_id,appsflyer_id=appsflyer_id).exists():
            obj=Install_DataPush.objects.create(
                appsflyer_id=appsflyer_id,
                app_id=app_id,
                campaign_name=campaign,
                media_source=data.get('media_source'),
                install_time=install_time_aware,
                install_date=install_date_aware,
                platform=data.get('platform'),
                city=data.get('city'),
                country=data.get('country'),
                device=data.get('device'),
                inserted_time=timezone.now(),
                reporttype=data.get('event_name'),
            )
        
            
        
        return Response({"message": "Data received "}, status=status.HTTP_201_CREATED)
