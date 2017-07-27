# MySQL to CloudWatch Logs [![Build Status](https://travis-ci.org/GSA/mysql_to_cloudwatch.svg?branch=master)](https://travis-ci.org/GSA/mysql_to_cloudwatch)

This is a script that grabs logs from MySQL and sends them to CloudWatch Logs.

## Setup

1. Enable the desired logs. The script will attempt to do so for you, but may fail (gracefully), based on if the user has permissions or not. More information:
    * [Amazon Web Services (AWS) Relational Database Service (RDS)](http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.Concepts.MySQL.html)
    * [MySQL (self-hosted)](https://dev.mysql.com/doc/refman/5.7/en/server-logs.html)
1. Create [a `.env` file](https://docs.docker.com/compose/environment-variables/#the-env-file) with your AWS connection information and other environment variables. See [`docker-compose.yml`](docker-compose.yml) for the list of supported variables.
1. TODO

## Running tests

```sh
cd tests

docker-compose up mysql
# this will print out a bunch of junk you can probably ignore

# in another terminal
docker-compose run tests
```

## Troubleshooting

If you get an error about "signature expired" or anything else related to timing, it is a [clock drift bug in Docker](https://forums.docker.com/t/time-in-container-is-out-of-sync/16566). Restart Docker for Mac/Windows.

## See also

* [Copying RDS logs to S3](https://github.com/ryanholland/rdslogs_to_s3)
