import json
import allure
from datetime import datetime
import pytest
from allure_commons.types import Severity

from conftest import service
from tests.resources.constants import timestamp_threshold
from demo_api_tests.models.helpers import return_full_path, send_request_api, validate_json_against_schema, \
    verify_response_code

pytestmark = [
    allure.label('layer', 'API test'),
    allure.label('owner', 'alexander_varaksa'),
    allure.epic('Reqres API'),
    allure.tag('REST')
]


@allure.title('Verify users per_page value')
@allure.feature('Get Users Per page')
@allure.story('Get User List')
@allure.severity(Severity.CRITICAL)
@pytest.mark.parametrize('users_per_page', [1, 6, 20])
def test_users_per_page(users_per_page):
    per_page = users_per_page

    response = send_request_api(
        service,
        "get",
        url=f"/users",
        params={"per_page": per_page}
    )
    verify_response_code(response, 200)
    with allure.step(f"verify per_page value is {per_page}"):
        assert response.json()['per_page'] == per_page
    if per_page > 12:
        per_page = 12
    with allure.step(f"verify item amount in data node is {per_page}"):
        assert len(response.json()['data']) == per_page


@allure.title('Verify GET users schema')
@allure.feature('Get User List')
@allure.story('Get User List')
@allure.severity(Severity.CRITICAL)
def test_users_schema():
    response = send_request_api(
        service,
        "get",
        f"/users")

    verify_response_code(response, 200)
    validate_json_against_schema('get_users.json', response.json())


@allure.title('Create user')
@allure.feature('Create user')
@allure.story('Post')
@allure.severity(Severity.CRITICAL)
def test_create_user():
    response = send_request_api(
        service,
        "post",
        url=f"/users",
        json={
            "name": "morpheus",
            "job": "leader"
        }
    )
    verify_response_code(response, 201)
    with allure.step(f"verify user name"):
        assert response.json()['name'] == "morpheus"
    with allure.step(f"verify job"):
        assert response.json()['job'] == "leader"


@allure.title('Create user with invalid json')
@allure.feature('Create user')
@allure.story('Post')
@allure.severity(Severity.MINOR)
def test_create_user_with_invalid_json():
    response = send_request_api(
        service,
        "post",
        url=f"/users",
        headers={'Content-Type': 'application/json'},
        data="{\"name\": \"morpheus, \"job\": \"leader\"}"
    )
    verify_response_code(response, 400)
    with allure.step(f'Verify response text contains <Bad Request>'):
        assert 'Bad Request' in response.text


@allure.title('Verify that duplicate user can be created and verify user schema and timestamp')
@allure.feature('Create user')
@allure.story('Post')
@allure.severity(Severity.CRITICAL)
# timestamp verification is rough due to not precise server time
def test_create_duplicate_user_schema_timestamp():
    timestamp_before = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")

    response = send_request_api(
        service,
        "post",
        url="/users",
        json={
            "name": "morpheus",
            "job": "leader"
        }
    )

    verify_response_code(response, 201)
    validate_json_against_schema('create_user.json', response.json())

    timestamp_before = datetime.strptime(timestamp_before, "%Y-%m-%dT%H:%M:%S.%f")
    timestamp_response = datetime.strptime(response.json()['createdAt'][:-1], "%Y-%m-%dT%H:%M:%S.%f")

    with allure.step(f"verify timestamp is within threshold"):
        assert abs((timestamp_response - timestamp_before).total_seconds()) < timestamp_threshold


@allure.title('Get user and validate response')
@allure.feature('Get User')
@allure.story('Get')
@allure.severity(Severity.CRITICAL)
def test_get_single_user():
    user_id_to_test = 2
    response = send_request_api(
        service,
        "get",
        url=f"/users/{user_id_to_test}",
    )

    with open(return_full_path('resources', 'files', 'jsons_reqres', 'user_id_2.json')) as file:
        sample_json = json.loads(file.read())
    with allure.step(f"verify response json same as sample json for user"):
        assert response.json() == sample_json


@allure.title('Delete user')
@allure.feature('Delete User')
@allure.story('Delete')
@allure.severity(Severity.CRITICAL)
def test_delete_user(create_test_user):
    user_id = create_test_user
    response = send_request_api(
        service,
        "delete",
        url=f"/users/{user_id}",
    )
    verify_response_code(response, 204)
    with allure.step(f"verify response text is empty"):
        assert response.text == ""


@allure.title('Delete user with non-existent id')
@allure.feature('Delete User')
@allure.story('Delete')
@allure.severity(Severity.MINOR)
def test_delete_user_invalid_id():
    user_id = "999999999999"
    response = send_request_api(
        service,
        "delete",
        url=f"/users/{user_id}",
    )
    verify_response_code(response, 204)
    with allure.step(f"verify response text is empty"):
        assert response.text == ""


@allure.title('Delete user with non-existent id with special symbols')
@allure.feature('Delete User')
@allure.story('Delete')
@allure.severity(Severity.MINOR)
def test_delete_user_invalid_id_spec_symbols():
    user_id = "~!$#@&%()*:{}?><"
    response = send_request_api(
        service,
        "delete",
        url=f"/users/{user_id}",
    )
    verify_response_code(response, 204)
    with allure.step(f"verify response text is empty"):
        assert response.text == ""


@allure.title('Update user and validate response against json schema')
@allure.feature('Update User')
@allure.story('Put')
@allure.severity(Severity.CRITICAL)
def test_update_user_schema(create_test_user):
    user_id = create_test_user
    response = send_request_api(
        service,
        "put",
        url=f"/users/{user_id}",
        json={
            "name": "morpheus",
            "job": "zion resident"
        }
    )
    verify_response_code(response, 200)
    validate_json_against_schema('update_user.json', response.json())


@allure.title('Update user via put request with empty json and validate against schema')
@allure.feature('Update User')
@allure.story('Put')
@allure.severity(Severity.MINOR)
def test_update_user_empty_json(create_test_user):
    user_id = create_test_user
    response = send_request_api(
        service,
        "put",
        url=f"/users/{user_id}",
        json={
        }
    )
    verify_response_code(response, 200)
    validate_json_against_schema('update_user_empty_json.json', response.json())


@allure.title('Update user via patch request and validate against json schema')
@allure.feature('Update User')
@allure.story('Patch')
@allure.severity(Severity.CRITICAL)
def test_update_user_patch_schema(create_test_user):
    user_id = create_test_user
    response = send_request_api(
        service,
        "patch",
        url=f"/users/{user_id}",
        json={
            "name": "morpheus",
            "job": "zion resident"
        }
    )
    verify_response_code(response, 200)
    validate_json_against_schema('update_user.json', response.json())


@allure.title('Update user via patch request with empty json')
@allure.feature('Update User')
@allure.story('Patch')
@allure.severity(Severity.MINOR)
def test_update_user_patch_empty_json_(create_test_user):
    user_id = create_test_user
    response = send_request_api(
        service,
        "patch",
        url=f"/users/{user_id}",
        json={
        }
    )
    verify_response_code(response, 200)
    validate_json_against_schema('update_user_empty_json.json', response.json())
