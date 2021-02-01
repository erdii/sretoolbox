"""
Caching helper decorator
"""

import functools
import weakref

_CACHES = weakref.WeakKeyDictionary()


def static(key):
    """
    Decorates a class method to look up and cache the execution result.

    Cache access is scoped by 2 things: class instance and `key`

    :param key: static cache key
    :type key: string
    """
    def decorate(func):
        @functools.wraps(func)
        def with_cache_get(self, *args, **kwargs):
            cache = _lazy_init(self)
            value = None
            try:
                value = cache[key]
            except KeyError:
                value = func(self, *args, **kwargs)
                cache[key] = value
            return value
        return with_cache_get
    return decorate


def computed(key_func):
    """
    Decorates a class method to look up and cache the execution result.

    Cache access is scoped by 2 things:
    class instance and the result of `key_func`.
    All *args and **kwargs (except `self`) are passed to this function
    and the return value is used as cache key.

    :param key_func: function to compute cache key
    :type key: function
    """
    def decorate(func):
        @functools.wraps(func)
        def with_cache_computed(self, *args, **kwargs):
            key = key_func(*args, **kwargs)

            cache = _lazy_init(self)
            value = None
            try:
                value = cache[key]
            except KeyError:
                value = func(self, *args, **kwargs)
                cache[key] = value
            return value
        return with_cache_computed
    return decorate


def remove_static(key):
    """
    Decorates a class method to remove the specified
    static cache key before execution
    """
    def decorate(func):
        @functools.wraps(func)
        def with_cache_remove_static(self, *args, **kwargs):
            raw_remove(self, key)
            return func(self, *args, **kwargs)
        return with_cache_remove_static
    return decorate


def remove_computed(key_func):
    """
    Decorates a class method to remove the specified
    computed cache key before execution
    """
    def decorate(func):
        @functools.wraps(func)
        def with_cache_remove_computed(self, *args, **kwargs):
            key = key_func(*args, **kwargs)
            raw_remove(self, key)
            return func(self, *args, **kwargs)
        return with_cache_remove_computed
    return decorate


def replace_static(key):
    """
    Decorates a class method to replace the
    specified static cache key with it's returned value
    """
    def decorate(func):
        @functools.wraps(func)
        def with_cache_replace_static(self, *args, **kwargs):
            value = func(self, *args, **kwargs)
            raw_set(self, key, value)
            return value
        return with_cache_replace_static
    return decorate


def replace_computed(key_func):
    """
    Decorates a class method to replace the
    specified computed cache key with it's returned value
    """
    def decorate(func):
        @functools.wraps(func)
        def with_cache_replace_computed(self, *args, **kwargs):
            key = key_func(*args, **kwargs)
            value = func(self, *args, **kwargs)
            raw_set(self, key, value)
            return value
        return with_cache_replace_computed
    return decorate


def raw_set(owner_ref, key, value):
    """
    raw_set exposes direct access to the cache.
    pass a reference to an class instance that has @cache.init on it
    """
    cache = _lazy_init(owner_ref)
    cache[key] = value


def raw_get(owner_ref, key):
    """
    raw_get exposes direct access to the cache.
    pass a reference to an class instance that has @cache.init on it
    """
    cache = _lazy_init(owner_ref)
    return cache[key]


def raw_remove(owner_ref, key):
    """
    raw_remove exposes direct access to remove a key from the cache
    pass a reference to an class instance that has @cache.init on it
    """
    cache = _lazy_init(owner_ref)

    try:
        del cache[key]
    except KeyError:
        pass


def _lazy_init(owner_ref):
    """
    Ensures/initializes a dedicated cache dict for `owner_ref`.

    :param owner_ref: instance of class with cache-decorated member functions
    :type owner_ref: any
    """
    if owner_ref in _CACHES:
        cache = _CACHES[owner_ref]
    else:
        cache = {}
        _CACHES[owner_ref] = cache
    return cache
