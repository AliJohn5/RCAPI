# storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage
from botocore.client import Config

class BackblazeB2Storage(S3Boto3Storage):
    def __init__(self, **settings):
        # Disable checksums explicitly
        settings['config'] = Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'},
            request_checksum_calculation=None,  # Disable checksum calculation
            response_checksum_validation=None  # Disable checksum validation
        )
        super().__init__(**settings)

    def _get_write_parameters(self, name, content):
        params = super()._get_write_parameters(name, content)
        # Remove problematic headers
        params.pop('ChecksumAlgorithm', None)
        params.pop('x-amz-sdk-checksum-algorithm', None)
        return params