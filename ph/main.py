import click
import logging
import os

from ph.utils.flags import create_flag, list_flags
from .utils.auth import auth, delete_token_from_file
from rich.logging import RichHandler
from rich.console import Console

console = Console()
logger = logging.getLogger('ph')

@click.group()
def main():
    """Posthog CLI"""
    setup_logger()

@main.command()
def logout():
    logger.debug("Logout")
    delete_token_from_file()

@main.command()
def login():
    logger.debug("Login")
    auth()

@click.group()
def flags():
    pass

@flags.command()
def list():
    logger.debug("List flags")
    list_flags()    

@flags.command()
@click.argument('key')
@click.option('-d', '--description', default="", help='Desc/Name of the flag')
@click.option('-p', '--rollout-percentage', default=100, help='Rollout percentage of the flag')
def create(key, description, rollout_percentage):
    logger.debug("Create flag")
    create_flag(key, description, rollout_percentage)

def setup_logger():
    # Set the log level for the root logger to NOTSET (this is required to allow handlers to control the logging level)
    logging.root.setLevel(logging.NOTSET)

    # Configure your application's logger
    log_level_name = os.getenv('PH_LOG_LEVEL', 'INFO').upper()
    app_log_level = getattr(logging, log_level_name, logging.INFO)

    # Setup the 'ph' logger to use RichHandler with the shared console instance
    logger = logging.getLogger('ph')
    logger.setLevel(app_log_level)
    rich_handler = RichHandler(
        console=console, show_time=False, show_level=True, show_path=False)
    rich_handler.setLevel(app_log_level)
    # Replace any default handlers with just the RichHandler
    logger.handlers = [rich_handler]

    # Set higher logging level for noisy libraries
    logging.getLogger('boto3').setLevel(logging.INFO)
    logging.getLogger('botocore').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)


main.add_command(flags)

if __name__ == "__main__":
    main()
