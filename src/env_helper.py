def get_db_kwargs(env):
    # adapted from https://gist.github.com/afeld/79d82d70a7cee21b92b43165b4c79c54

    db_kwargs = {'db': 'mysql'}
    # optional database connection information
    for key in ['host', 'user', 'passwd', 'port']:
        env_var = "DB_{}".format(key.upper())
        if env_var in env:
            db_kwargs[key] = env[env_var]

    return db_kwargs
