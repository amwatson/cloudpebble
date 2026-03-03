import mimetypes

from botocore.exceptions import ClientError
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_safe

import utils.s3 as s3


@require_safe
def s3_builds_proxy(request, path):
    """Proxy build artifacts from the S3/R2 builds bucket.

    Used so that MEDIA_URL can point to the web server itself, avoiding
    the need to expose the S3 bucket directly.  URLs are UUID-based so
    no authentication is required (same security model as the old nginx
    proxy to fake-S3).
    """
    try:
        data = s3.read_file('builds', path)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return HttpResponseNotFound()
        raise

    content_type, _ = mimetypes.guess_type(path)
    if content_type is None:
        content_type = 'application/octet-stream'

    response = HttpResponse(data, content_type=content_type)
    response['Access-Control-Allow-Origin'] = '*'
    return response
