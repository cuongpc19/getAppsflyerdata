# myapp/admin.py
from django.contrib import admin
from .models import Install_Data # Import model của bạn

admin.site.register(Install_Data)