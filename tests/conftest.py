import subprocess

import pytest

@pytest.fixture(scope='session', autouse=True)
def ensure_awslocal():
    try:
        subprocess.check_call(['awslocal', 's3', 'ls'])
    except subprocess.CalledProcessError:
        raise AssertionError('AWS localstack is not started. Try `docker-compose up -d`')