# File: store/backends/s3boto3.py
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    """
    Custom S3 storage class for media files
    """
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    
    # Media files configuration
    location = 'media'  # This creates a 'media' folder in your S3 bucket
    default_acl = None
    file_overwrite = False
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"MediaStorage initialized with bucket: {self.bucket_name}")
        print(f"Location: {self.location}")
        print(f"Custom domain: {self.custom_domain}")