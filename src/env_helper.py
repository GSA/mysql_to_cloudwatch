def get_db_kwargs(env):
    """http://mysqlclient.readthedocs.io/en/latest/user_guide.html#functions-and-attributes"""

    db_kwargs = {
        'host': env['DB_HOST'],
        'db': 'mysql'
    }

    # optional database connection information
    for key in ['user', 'passwd', 'port']:
        env_var = "DB_{}".format(key.upper())
        if env_var in env:
            db_kwargs[key] = env[env_var]

    return db_kwargs
