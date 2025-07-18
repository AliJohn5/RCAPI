import os
import random
import string
import tempfile
from datetime import datetime, timedelta, timezone
from django.conf import settings
from b2sdk.v2 import B2Api, InMemoryAccountInfo


def generate_random_string(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def upload_image_to_backblaze(file, existing_image=None, bucket_name=settings.AWS_STORAGE_BUCKET_NAME):
    if existing_image:
        existing_image.delete()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)
        temp_file_path = temp_file.name

    # Setup B2 API
    app_id = settings.AWS_ACCESS_KEY_ID
    app_key = settings.AWS_SECRET_ACCESS_KEY
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account('production', app_id, app_key)

    bucket = b2_api.get_bucket_by_name(bucket_name)

    
    now = datetime.now(timezone.utc)
    folder_path = now.strftime("photos/%Y/%m/%d")
    random_filename = generate_random_string(15)
    full_file_name = f"{folder_path}/{random_filename}"

    uploaded_file = bucket.upload_local_file(
        local_file=temp_file_path,
        file_name=full_file_name,
        content_type='auto'
    )

    os.remove(temp_file_path)

    # 🔐 Generate signed URL valid for 30 days
    auth_token = bucket.get_download_authorization(
        file_name_prefix=full_file_name,
        valid_duration_in_seconds=24 * 60 * 60 * 6 
    )
    base_url = b2_api.get_download_url_for_file_name(bucket_name, full_file_name)
    signed_url = f"{base_url}?Authorization={auth_token}"

    return {
        "file_name": full_file_name,  # includes folders
        "signed_url": signed_url
    }



def get_b2_signed_url(file_name, duration_seconds=86400*6):  # 86400 = 24 hours
    """
    Generate a signed download URL for a file stored in Backblaze B2.
    
    :param file_name: The full path or name of the file in the B2 bucket.
    :param duration_seconds: Duration for which the signed URL is valid.
    :return: A signed URL string.
    """
    app_id = settings.AWS_ACCESS_KEY_ID
    app_key = settings.AWS_SECRET_ACCESS_KEY
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account('production', app_id, app_key)

    bucket = b2_api.get_bucket_by_name(bucket_name)

    # Generate a download auth token for a specific file
    auth_token = bucket.get_download_authorization(
        file_name_prefix=file_name,
        valid_duration_in_seconds=duration_seconds
    )

    # Generate the base download URL
    base_url = b2_api.get_download_url_for_file_name(bucket_name, file_name)

    # Return the signed URL
    return f"{base_url}?Authorization={auth_token}"