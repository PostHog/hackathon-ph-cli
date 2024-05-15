import logging
import requests
import os
import json

logger = logging.getLogger('ph')

CREDENTIALS_FILE = os.path.expanduser('~/.posthog/credentials.json')

def save_token_to_file(token):
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump({"credentials": {"app.dev.posthog.dev": {"token": token, "organization": "", "project": ""}}}, file)


def read_token_from_file():
    try:
        with open(CREDENTIALS_FILE, 'r') as file:
            data = json.load(file)
            return data["credentials"]["app.dev.posthog.dev"]["token"]
    except (FileNotFoundError, KeyError):
        return None

def delete_token_from_file():
    try:
        if os.path.exists(CREDENTIALS_FILE):
            os.remove(CREDENTIALS_FILE)
    except Exception as e:
        logger.error(f"Failed to delete token from file: {e}")


def get_url(api_part):
    api_protocol = os.environ.get('PH_API_PROTOCOL_WEB', 'https')
    api_host = os.environ.get('PH_API_HOST_WEB', 'app.dev.posthog.dev')
    api_port = os.environ.get('PH_API_PORT_WEB', '')
    if api_port:
        api_port = f":{api_port}"
    return f"{api_protocol}://{api_host}{api_port}/{api_part}"

def get_headers():
    api_token = os.environ.get('PH_API_TOKEN')
    if not api_token:
        api_token = read_token_from_file()

    if not api_token:
        auth_url = get_url('organization/apikeys')
        api_token = prompt_for_token(auth_url)
        if api_token:
            os.environ['PH_API_TOKEN'] = api_token
            save_token_to_file(api_token)
        else:
            logger.error("No token provided.")
            exit()

    return {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + api_token
    }


def prompt_for_token(auth_url):
    print("\033[1;96mPlease authenticate by visiting the following URL:\033[0m")
    print(auth_url)
    print("\033[1;96mAfter obtaining the token, please enter it below:\033[0m")
    return input("Token: ")


def get_headers():
    api_token = os.environ.get('PH_API_TOKEN')
    if not api_token:
        api_token = read_token_from_file()

    if not api_token:
        auth_url = get_url('organization/apikeys')
        api_token = prompt_for_token(auth_url)
        if api_token:
            os.environ['PH_API_TOKEN'] = api_token
            save_token_to_file(api_token)
        else:
            logger.error("No token provided.")
            exit()

    return {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + api_token
    }


def auth():
    """Authenticate the user."""
    headers = get_headers()

    # validate if account is active
    url = get_url('project/2/settings/project-details')
    logger.debug(f"Validating account... {url} {headers}")
    payload={}
    response = requests.get(url, headers=headers, params=payload)
    print(response.status_code)
    # if response.status_code == 200:
    #     print(response.json())
    #     data = response.json()
    #     logger.info(data)
    # elif response.status_code == 401:
    #     logger.error(f"{response.status_code} Invalid token provided.")
    #     delete_token_from_file()
    #     exit(-1)
    # else:
    #     logger.error(f"Error: {response.status_code}")
    #     exit(-1)

