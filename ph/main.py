import click
import logging
import os
from .utils.auth import auth, delete_token_from_file
from rich.logging import RichHandler
from rich.console import Console

console = Console()

@click.command()
@click.argument('mode', type=click.Choice(['login', 'flags', 'logout']))
def main(mode):
    """Posthog CLI"""
    setup_logger()
    logger = logging.getLogger('ph')

    if mode == 'logout':
        logger.debug("Logout selected")
        delete_token_from_file()
    elif mode == 'login':
        logger.debug("Login mode selected")
        auth()
    elif mode == 'flags':
        logger.debug("Flags mode selected")
    else:
        logger.error("Invalid mode selected")


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


if __name__ == "__main__":
    main()

