# MySQL to CloudWatch Logs [![Build Status](https://travis-ci.org/GSA/mysql_to_cloudwatch.svg?branch=master)](https://travis-ci.org/GSA/mysql_to_cloudwatch)

This is a script that grabs logs from MySQL and sends them to CloudWatch Logs.

## Setup

1. Enable the desired logs. More information:
    * [Amazon Web Services (AWS) Relational Database Service (RDS)](http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.Concepts.MySQL.html)
    * [MySQL (self-hosted)](https://dev.mysql.com/doc/refman/5.7/en/server-logs.html)
1. Create [a `.env` file](https://docs.docker.com/compose/environment-variables/#the-env-file) with your AWS connection information and other environment variables. See [`docker-compose.yml`](docker-compose.yml) for the list of supported variables.
1. TODO

## Running tests

```sh
cd tests

docker-compose up -d mysql
# alternatively, run in a separate terminal without the `-d`

docker-compose up tests
```

## See also

* [Copying RDS logs to S3](https://github.com/ryanholland/rdslogs_to_s3)
