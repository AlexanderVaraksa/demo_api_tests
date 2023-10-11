import pytest
import logging
from tests.resources.constants import reqres_url

service = reqres_url

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@pytest.fixture(scope='function', autouse=False)
def create_test_user():
    from demo_api_tests.models.helpers import send_request_api
    response = send_request_api(
        service,
        "post",
        url="/users",
        json={
            "name": "morpheus",
            "job": "leader"
        }
    )
    user_id = response.json()['id']

    return user_id
