from b2sdk.v2 import InMemoryAccountInfo, B2Api
from django.conf import settings
import os

from django.http import FileResponse, Http404

def get_b2_api():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", settings.B2_ACCOUNT_ID, settings.B2_APPLICATION_KEY)
    return b2_api

def serve_private_media(request, file_path):
    try:
        b2_api = get_b2_api()
        bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
        download_url = bucket.get_download_url_by_name(file_path)
        # Or use bucket.get_file_info_by_name(file_path) and stream
        return FileResponse(download_url, as_attachment=True)
    except Exception:
        raise Http404("File not found or access denied")
    