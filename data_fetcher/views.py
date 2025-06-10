# myapp/views.py
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Install_Data
from .serializers import DataInstallSerializer # <-- Import serializer mới

class GetCampaignByAppsflyerIDAPIView(APIView):
    """
    API View để chỉ trả về trường 'campaign' dựa trên appsflyerID.
    """
    def get(self, request, appsflyer_id):
        # 1. Kiểm tra dữ liệu trên DB bằng appsflyerID
        # get_object_or_404 vẫn hoạt động bình thường với khóa chính
        appflyer_data = get_object_or_404(Install_Data, appsflyer_id=appsflyer_id)

        # 2. Chuyển đổi đối tượng bằng DataInstallSerializer
        serializer = DataInstallSerializer(appflyer_data)

        # 3. Trả về Response cho client
        # serializer.data sẽ chỉ chứa {'campaign': 'Giá trị của campaign'}
        return Response(serializer.data, status=status.HTTP_200_OK)