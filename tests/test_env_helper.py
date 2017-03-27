from ..src import env_helper

def test_empty():
    result = env_helper.get_db_kwargs({})
    assert result == {'db': 'mysql'}

def test_optional():
    env = {
        'DB_HOST': 'foo.com',
        'DB_USER': 'jane'
    }
    result = env_helper.get_db_kwargs(env)
    assert result == {
        'host': 'foo.com',
        'db': 'mysql',
        'user': 'jane'
    }

def test_junk():
    env = {'DB_OTHER': 'foo'}
    result = env_helper.get_db_kwargs(env)
    assert result == {'db': 'mysql'}
