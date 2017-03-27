FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

VOLUME /usr/src/app

ENTRYPOINT ["/usr/src/app/src/wait-for-it.sh", "mysql:3306", "-t", "25", "-s", "--"]
CMD ["python3", "mysql_to_cloudwatch.py"]
