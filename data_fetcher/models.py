from django.db import models

# Create your models here.
class Install_Data(models.Model):
    appsflyer_id = models.CharField(max_length=255, null = False, unique=True)
    advertising_id = models.CharField(max_length=255, null = True)
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
            models.Index(fields=['campaign_name']),
            models.Index(fields=['install_date']),
            models.Index(fields=['platform']),
            models.Index(fields=['appsflyer_id']),
            models.Index(fields=['country']),
            models.Index(fields=['media_source']),
            models.Index(fields=['is_get_data'])
        ]