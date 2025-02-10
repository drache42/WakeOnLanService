import logging.config

def get_logging_config(debug_mode: bool) -> dict:
    """
    Returns a logging configuration dictionary based on the debug mode.
    
    Args:
        debug_mode (bool): If True, sets the logging level to DEBUG, otherwise INFO.
    
    Returns:
        dict: A dictionary containing the logging configuration.
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG' if debug_mode else 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console'],
                'level': 'DEBUG' if debug_mode else 'INFO',
                'propagate': True
            },
        }
    }

def setup_logging(debug_mode):
    """
    Sets up logging configuration based on the debug mode.
    
    Args:
        debug_mode (bool): If True, sets the logging level to DEBUG, otherwise INFO.
    """
    logging_config = get_logging_config(debug_mode)
    logging.config.dictConfig(logging_config)