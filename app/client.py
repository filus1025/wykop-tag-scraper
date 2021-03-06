import hashlib
import requests
import logging
from config import Config
from string import Template
from app.model import ApiResponse


TAGS_ENTRIES_BASE_URI_TEMPLATE = Template("https://a2.wykop.pl/Tags/Entries/$tag/page/$page/appkey/$appkey")

logger = logging.getLogger(__name__)


def fetch_tag_page(tag, page=1):
    u = TAGS_ENTRIES_BASE_URI_TEMPLATE.substitute(tag=tag, page=page, appkey=Config.APP_KEY)
    r = _get_for_url_with_retry(u, 3)
    r.raise_for_status
    body = r.json()

    return ApiResponse(body)


def fetch_next_page(url):
    r = _get_for_url_with_retry(url, 3)
    r.raise_for_status
    body = r.json()

    return ApiResponse(body)


def _get_for_url_with_retry(url, retry_count):
    for i in range(1, retry_count + 1):
        try:
            return _get_for_url(url)
        except requests.exceptions.Timeout:
            logger.warn(f'Request timed out, fail count: {i}')
            pass
        except requests.exceptions.ConnectionError:
            logger.warn(f'Request failed due to connection error, fail count: {i}')
            pass
    logger.error('Requesting {url} failed to many times')
    raise RuntimeError('Requesting {url} failed to many times')


def _get_for_url(url):
    h = {"apisign": _generate_signature(url)}
    response = requests.get(url=url, headers=h, timeout=10)

    return response


def _generate_signature(endpoint_url):
    signature_string = f'{Config.APP_SECRET}{endpoint_url}'
    return hashlib.md5(signature_string.encode('utf-8')).hexdigest()
