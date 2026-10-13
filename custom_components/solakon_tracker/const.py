from datetime import timedelta

DOMAIN = "solakon_tracker"
CONF_HOST = "host"
DEFAULT_HOST = "http://192.168.188.114"
STATUS_PATH = "/api/v1/status"
UPDATE_INTERVAL = timedelta(seconds=30)