from ..src import env_helper

def test_bare_minimum():
    env = {'DB_HOST': 'foo.com'}
    result = env_helper.get_db_kwargs(env)
    assert result == {
        'host': 'foo.com',
        'db': 'mysql'
    }

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
