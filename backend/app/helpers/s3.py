# Backwards-compatibility shim – S3 client now lives in app.aws.client
from app.aws.client import generate_presigned_put_url, get_s3_client, upload_file_to_r2 as upload_r2_file  # noqa: F401
