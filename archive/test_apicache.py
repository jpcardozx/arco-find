import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.api_service import APICache


def test_apicache_set_and_get():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = APICache(cache_dir=tmpdir, ttl_seconds=60)
        url = 'https://example.com/api'
        params = {'q': 'test'}
        data = {'result': 42}
        cache.set(url, params, data)
        assert cache.get(url, params) == data


def test_apicache_expiration():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = APICache(cache_dir=tmpdir, ttl_seconds=0)
        url = 'https://example.com/api'
        params = {'q': 'test'}
        data = {'result': 42}
        cache.set(url, params, data)
        assert cache.get(url, params) is None
