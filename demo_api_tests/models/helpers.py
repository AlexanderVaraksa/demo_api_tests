import json
import os

import allure
from requests import sessions
from allure_commons.types import AttachmentType
from curlify import to_curl
from jsonschema.validators import validate

import tests


def send_request_api(service, method, url, **kwargs):
    new_url = service + url
    method = method.upper()
    with allure.step(f" {method} {service}{url} body/params: {kwargs}"):
        with sessions.Session() as session:
            response = session.request(method=method, url=new_url, **kwargs)
            message = to_curl(response.request)

            allure.attach(body=message.encode("utf8"), name="Curl", attachment_type=AttachmentType.TEXT,
                          extension='txt')

        if not response.content:
            allure.attach(body='empty response', name='Empty Response', attachment_type=AttachmentType.TEXT,
                          extension='txt')
        elif 'text/html' in response.headers['Content-Type']:
            allure.attach(body=response.content, name='Text/HTML Response', attachment_type=AttachmentType.TEXT,
                          extension='txt')
        elif 'application/json' in response.headers['Content-Type']:
            allure.attach(body=json.dumps(response.json(), indent=4).encode("utf-8"), name="Response Json",
                          attachment_type=AttachmentType.JSON, extension='json')
    return response


def return_full_path(*file_path):
    return os.path.abspath(os.path.join(os.path.dirname(tests.__file__), *file_path))


def validate_json_against_schema(file_name_schema, response_json):
    with open(return_full_path('resources', 'files', 'json_schemas_reqres', file_name_schema)) as file:
        schema = json.loads(file.read())
    with allure.step(f"validate response json with schema from file: {file_name_schema}"):
        validate(instance=response_json, schema=schema)


def verify_response_code(response, response_code):
    with allure.step(f"verify status code is: {response_code}"):
        assert response.status_code == response_code
