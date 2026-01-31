from django.urls import path
from .views import GetCampaignByAppsflyerIDAPIView  # Import view
from .views import GetDataPullByAppsflyerView

urlpatterns = [
    # API lấy trường campaign theo appsflyer_id
    path('appflyerdata/<str:appsflyer_id>/campaign/', GetCampaignByAppsflyerIDAPIView.as_view(), name='get-campaign-by-id'),
    path('appflyerdata/<str:appsflyer_id>/campaign/<str:app_name>/<str:platform_id>', GetCampaignByAppsflyerIDAPIView.as_view(), name='get-campaign-app'),
    path('appflyerdata/pull/', GetDataPullByAppsflyerView.as_view(), name='appsflyer-pull'),
]