import os
import json
from contextlib import ContextDecorator
from tempfile import TemporaryDirectory
from uuid import uuid4

from django.core.cache import cache


class DiskCache(ContextDecorator):
    """Context manager to cache key/values on disk optionally having Django
    cache (usually in memory) as in intermediary for faster resuts."""

    def __init__(self, expires_in_memory=None):
        self.uuid = str(uuid4())
        self.cache = cache
        self.tmp = TemporaryDirectory()
        self.expires_in_memory = expires_in_memory

    def _key(self, keys):
        """Given a sequence of keys, returns a single key as a string"""
        key = os.sep.join(str(k) for k in keys)
        return os.path.join(self.uuid, key)

    def _path(self, keys):
        """Given a sequence of keys, returns the path for that file in disk"""
        path = os.path.join(self.tmp.name, self._key(keys))
        directory, _ = os.path.split(path)
        os.makedirs(directory, exist_ok=True)
        return path

    def set(self, keys, value):
        """Given a sequence of keys, creates the file"""
        with open(self._path(keys), 'w') as fobj:
            fobj.write(json.dumps(value))

    def get(self, keys):
        """Given a sequence of keys, retrieves the value"""
        key = self._key(keys)
        cached = self.cache.get(key)
        if cached:
            return cached

        path = self._path(keys)
        if not os.path.exists(path):
            return None

        with open(path) as fobj:
            value = json.loads(fobj.read())

        if self.expires_in_memory:  # disallow non-specified expiration
            self.cache.set(key, value, self.expires_in_memory)

        return value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        cache.delete_pattern(f'{self.uuid}*')
        self.tmp.cleanup()
