import pytest
import memcache


def setget(mc_client, key, value):
    assert mc_client.set(key, value)
    assert value == mc_client.get(key)


def test_bad_host():
    """test that exception is raised for invalid host"""
    with pytest.raises(Exception) as e:
        assert memcache.Client('wrong.host.name')


def test_bad_port():
    """test that exception is raised for invalid port"""
    with pytest.raises(ConnectionError) as e:
        assert memcache.Client(port=11111)


def test_set_and_get():
    mc = memcache.Client()
    setget(mc, 'key_int', 1000)
    setget(mc, 'key_float', 10.0034)
    setget(mc, 'key_str', 'Это очень длинная строка, даже совсем-совсем длинная\r\n и в несколько строк!')
    setget(mc, 'key_bytes', b'0983urj303847380rfj0uj3i9jf048y734804urjfo3j904uf')
    setget(mc, 'key_list', ['test string', 123, b'test'])


# def test_bad_type():
#     mc = memcache.Client()
#     with pytest.raises(TypeError) as e:
#         assert setget(mc, 'key4', [1, 2, ])


def test_delete():
    mc = memcache.Client()
    test_key = 'test_key'
    setget(mc, test_key, 1000)
    assert mc.delete(test_key)
    assert not mc.delete(test_key)
    assert mc.get(test_key) is None
