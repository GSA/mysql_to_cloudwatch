# optional database connection information
# https://pymysql.readthedocs.io/en/latest/modules/connections.html
SUPPORTED_OPTS = [
    'host',
    'user',
    'password',
    'port',
    'unix_socket',
    'charset'
]

# adapted from https://gist.github.com/afeld/79d82d70a7cee21b92b43165b4c79c54
def get_db_kwargs(env):
    db_kwargs = {'db': 'mysql'}
    for key in SUPPORTED_OPTS:
        env_var = "DB_{}".format(key.upper())
        if env_var in env:
            db_kwargs[key] = env[env_var]

    return db_kwargs
