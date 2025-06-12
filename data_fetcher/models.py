from django.db import models

# Create your models here.
class Install_Data(models.Model):
    appsflyer_id = models.CharField(max_length=255, null = False, unique=True)
    app_id = models.CharField(max_length=255, null = True)
    campaign_name = models.CharField(max_length=255, null = True)
    install_time = models.DateTimeField()
    install_date = models.DateField()
    platform = models.CharField(max_length=50, null = True)
    city = models.CharField(max_length=50, null = True)
    country = models.CharField(max_length=50, null = True)
    device = models.CharField(max_length=255, null = True)
    media_source = models.CharField(max_length=255, null = True)
    inserted_time =  models.DateTimeField(null=True)
    is_get_data = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['app_id','appsflyer_id']),
        ]