import logging
from time import sleep
import requests
import os
import json
import inquirer
import webbrowser 

logger = logging.getLogger('ph')

CREDENTIALS_FILE = os.path.expanduser('~/.posthog/credentials.json')
PH_ENDPOINT = os.environ.get('PH_ENDPOINT', 'app.dev.posthog.dev')

def save_token_to_file(token, org, project):
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    data = {}
    try:
        with open(CREDENTIALS_FILE, 'r') as file:
            try:
                data = json.load(file)
            except Exception as e:
                pass
    except FileNotFoundError:
        pass

    credentials = data.get("credentials", {})
    endpoint = {"token": token, "organization": org, "project": project}
    credentials[PH_ENDPOINT] = endpoint
    data["credentials"] = credentials

    with open(CREDENTIALS_FILE, 'w') as file:
        try:
            json.dump(data, file)
        except Exception as e:
            return None

def read_token_from_file():
    try:
        with open(CREDENTIALS_FILE, 'r') as file:
            try:
                data = json.load(file)
            except Exception:
                return None
            return data["credentials"][PH_ENDPOINT]["token"]
    except (FileNotFoundError, KeyError):
        return None
    
def read_organization_from_file():
    try:
        with open(CREDENTIALS_FILE, 'r') as file:
            try:
                data = json.load(file)
            except Exception:
                return None
            return data["credentials"][PH_ENDPOINT]["organization"]
    except (FileNotFoundError, KeyError):
        return None
    
def read_project_from_file():
    try:
        with open(CREDENTIALS_FILE, 'r') as file:
            try:
                data = json.load(file)
            except Exception:
                return None
            return data["credentials"][PH_ENDPOINT]["project"]
    except (FileNotFoundError, KeyError):
        return None

def delete_token_from_file():
    try:
        if os.path.exists(CREDENTIALS_FILE):
            data = {}
            with open(CREDENTIALS_FILE, 'r') as file:
                try:
                    data = json.load(file)
                except Exception:
                    return
                if PH_ENDPOINT in data["credentials"]:
                    del data["credentials"][PH_ENDPOINT]
            with open(CREDENTIALS_FILE, 'w') as file:
                json.dump(data, file)

    except (FileNotFoundError, KeyError) as e:
        return

def get_url(api_part):
    api_protocol = os.environ.get('PH_API_PROTOCOL_WEB', 'https')
    api_port = os.environ.get('PH_API_PORT_WEB', '')
    if api_port:
        api_port = f":{api_port}"
    return f"{api_protocol}://{PH_ENDPOINT}{api_port}/{api_part}"

def get_token():
    api_token = os.environ.get('PH_API_TOKEN')
    if not api_token:
        api_token = read_token_from_file()

    if not api_token:
        api_token = prompt_for_token(PH_ENDPOINT)
        if api_token:
            os.environ['PH_API_TOKEN'] = api_token
            save_token_to_file(api_token, "", "")
        else:
            logger.error("No token provided.")
            exit()

    return api_token

def get_headers():
    return {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + get_token()
    }


def prompt_for_token(auth_url):
    print("\033[1;96mPlease authenticate by visiting the following URL:\033[0m")
    print(auth_url)
    print("\033[1;96mAfter obtaining the token, please enter it below:\033[0m")
    return input("Token: ")


def auth(switch_organization=False, switch_project=False):
    """Authenticate the user or switch organization or project."""
    headers = get_headers()

    # validate if account is active
    url = get_url('api/organizations')
    logger.debug(f"Validating account... {url} {headers}")
    response = requests.get(url, headers=headers, allow_redirects=False)
    if response.status_code == 200:
        data = response.json()
        org = read_organization_from_file()

        if not org or switch_organization:
            select_org(data)
        project = read_project_from_file()
        
        if not project or switch_project:
            list_project()
    else:
        if response.status_code == 401:
            logger.error(f"{response.status_code} Invalid token provided.")
        elif response.status_code == 302:
            logger.error(f"Redirection URL: {response.headers.get('Location')}")
        else:
            logger.error(f"Error: {response.status_code}")
        delete_token_from_file()
        exit(-1)

def create_token():
    url = get_url('api/login/cli/start')
    response = requests.post(url, allow_redirects=False)
    data = response.json()
    logger.info(f"data cli start: {data}")

    if response.status_code == 200:

        url = get_url('api/login/cli')
        response = requests.get(url, allow_redirects=False, params={"code": data.get('code')})
        data = response.json()
        logger.info(f"data login cli: {data}")

        if response.status_code == 200:
            confirm = data.get('confirm')
        else:
            logger.error(f"Error: {response.status_code}")
            return

        if confirm:
            webbrowser.open(confirm)

            while (True):
                url = get_url('api/login/cli/check')
                response = requests.get(url, allow_redirects=False, params={"code": data.get('code')})
                data = response.json()
                logger.info(f"data login check: {data}")

                if response.status_code == 200:
                    status = data.get('status')

                    if status == "authenticated":
                        access_token = data.get('access_token')
                        save_token_to_file(access_token, "", "")
                        break
                    else:
                        sleep(1)
                else:
                    logger.error(f"Error: {response.status_code}")
                    return
        else:
            logger.error("Error: Confirm URL not found.")
            return

    else:
        logger.error(f"Error: {response.status_code}")

def select_org(data):
    """Select the organization."""
    results = data.get('results')
    # TODO: name isnt unique
    display_to_id = {option['name']: option['id'] for option in results}
    choices = list(display_to_id.keys())

    questions = [
        inquirer.List('select_org',
                      message="Select organization",
                      choices=choices,
                      ),
    ]
    answers = inquirer.prompt(questions)
    selected_display = answers.get('select_org')
    selected_id = display_to_id[selected_display]
    logger.info(f"Selected organization: {selected_display}: {selected_id}")
    save_token_to_file(get_token(), selected_id, "")

def select_project(data):
    """Select the project."""
    results = data.get('results')
    display_to_id = {option['name']: option['id'] for option in results}
    choices = list(display_to_id.keys())

    questions = [
        inquirer.List('select_project',
                      message="Select project",
                      choices=choices,
                      ),
    ]
    answers = inquirer.prompt(questions)
    selected_display = answers.get('select_project')
    selected_id = display_to_id[selected_display]
    logger.info(f"Selected project: {selected_display}: {selected_id}")
    org = read_organization_from_file()
    save_token_to_file(get_token(), org, selected_id)

def list_project():
    """Select the project."""
    headers = get_headers()

    org = read_organization_from_file()
    url = get_url(f'api/organizations/{org}/projects')

    response = requests.get(url, headers=headers, allow_redirects=False)
    if response.status_code == 200:
        data = response.json()
        select_project(data)
    else:
        if response.status_code == 401:
            logger.error(f"{response.status_code} Invalid token provided.")
        elif response.status_code == 302:
            logger.error(f"Redirection URL: {response.headers.get('Location')}")
        else:
            logger.error(f"Error: {response.status_code}")
        delete_token_from_file()
        exit(-1)
