""" Tests for memcache"""

import pytest
import memcache


def check_set_get(mem_cache, key, value):
    """
    Checking set(), then get() and
    their equivalence to each other
    """
    assert mem_cache.set(key, value)
    assert mem_cache.get(key) == value


def test_bad_host():
    """test that exception is raised for invalid host"""
    with pytest.raises(Exception):
        assert memcache.Client('wrong.host.name')


def test_bad_port():
    """test that exception is raised for invalid port"""
    with pytest.raises(ConnectionError):
        assert memcache.Client(port=11111)


def test_set_and_get():
    """
    Checking set() of many types,
    then get() and their equivalence to each other
    """
    mem_cache = memcache.Client()
    check_set_get(mem_cache, 'key_int', 1000)
    check_set_get(mem_cache, 'key_float', 10.0034)
    check_set_get(
        mem_cache,
        'key_str',
        'Это очень длинная строка, даже совсем-совсем длинная'
        'и в несколько строк!')
    check_set_get(
        mem_cache,
        'key_bytes',
        b'0983urj303847380rfj0uj3i9jf048y734804urjfo3j904uf')
    check_set_get(mem_cache, 'key_list',
                  ['test string', 123, b'test'])


def test_delete():
    """ Test delete()"""
    mem_cache = memcache.Client()
    test_key = 'test_key'
    check_set_get(mem_cache, test_key, 1000)
    assert mem_cache.delete(test_key)
    assert not mem_cache.delete(test_key)
    assert mem_cache.get(test_key) is None
