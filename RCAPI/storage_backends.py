from b2sdk.v2 import InMemoryAccountInfo, B2Api
from django.core.files.storage import Storage
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
import mimetypes
import time
import urllib.parse


class B2PrivateMediaStorage(Storage):
    def __init__(self):
        info = InMemoryAccountInfo()
        self.b2_api = B2Api(info)
        self.bucket_name = settings.B2_BUCKET_NAME
        self.application_key_id = settings.B2_KEY_ID
        self.application_key = settings.B2_APPLICATION_KEY

        self.b2_api.authorize_account("production", self.application_key_id, self.application_key)
        self.bucket = self.b2_api.get_bucket_by_name(self.bucket_name)

    def _save(self, name, content):
        mime_type, _ = mimetypes.guess_type(name)
        file_bytes = content.read()
        self.bucket.upload_bytes(file_bytes, name, content_type=mime_type or 'application/octet-stream')
        return name

    def exists(self, name):
        try:
            self.bucket.get_file_info_by_name(name)
            return True
        except:
            return False

    def url(self, name):
        file_info = self.bucket.get_file_info_by_name(name)
        file_id = file_info.id_
        # Generate signed (temporary) download URL valid for 1 hour
        return self.b2_api.get_download_url_with_auth(file_id, int(time.time()) + 3600)
