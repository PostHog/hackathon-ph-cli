import inquirer
import requests
from ph.utils.auth import get_headers, get_url, read_project_from_file
import logging

logger = logging.getLogger('ph')

def list_flags():
    """List flags."""
    headers = get_headers()
    project_id = read_project_from_file()
    url = get_url(f'api/projects/{project_id}/feature_flags')
    response = requests.get(url, headers=headers, allow_redirects=False)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results')
        display_to_id = {option['name']: option['id'] for option in results}
        choices = list(display_to_id.keys())

        questions = [
            inquirer.List('select_flag',
                        message="Select flag",
                        choices=choices,
                        ),
        ]
        answers = inquirer.prompt(questions)
        selected_display = answers.get('select_flag')
        selected_id = display_to_id[selected_display]
        logger.info(f"Selected flag: {selected_display}: {selected_id}")
        load_flag(selected_id)
    else:
        if response.status_code == 401:
            logger.error(f"{response.status_code} Invalid token provided.")
        elif response.status_code == 302:
            logger.error(f"Redirection URL: {response.headers.get('Location')}")
        else:
            logger.error(f"Error: {response.status_code}")

def load_flag(id):
    """Load flag."""
    headers = get_headers()
    project_id = read_project_from_file()
    url = get_url(f'api/projects/{project_id}/feature_flags/{id}')
    response = requests.get(url, headers=headers, allow_redirects=False)
    if response.status_code == 200:
        data = response.json()
        logger.info(f"Flag data: {data}")
    else:
        if response.status_code == 401:
            logger.error(f"{response.status_code} Invalid token provided.")
        elif response.status_code == 302:
            logger.error(f"Redirection URL: {response.headers.get('Location')}")
        else:
            logger.error(f"Error: {response.status_code}")
