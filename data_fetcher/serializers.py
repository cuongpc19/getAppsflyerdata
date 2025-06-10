# myapp/serializers.py
from rest_framework import serializers
from .models import Install_Data

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Install_Data
        fields = ['campaign_name'] # Các trường bạn muốn trả về
