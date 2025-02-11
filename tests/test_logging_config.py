from wakeonlanservice.logging_config import get_logging_config

def test_get_logging_config_debug():
    config = get_logging_config(True)
    assert config["handlers"]["console"]["level"] == "DEBUG"
    assert config["loggers"][""]["level"] == "DEBUG"

def test_get_logging_config_info():
    config = get_logging_config(False)
    assert config["handlers"]["console"]["level"] == "INFO"
    assert config["loggers"][""]["level"] == "INFO"
