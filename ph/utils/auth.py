import logging

logger = logging.getLogger('ph')

def auth():
    """Authenticate the user."""
    logger.info( input("Token: ") )
    return True

