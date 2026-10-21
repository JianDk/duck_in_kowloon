"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "lost_in_kowloon.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 2
# The socket to bind
bind = "127.0.0.1:8000"
# Restart workers when code changes (development only!)
reload = False
# Write access and error info to /var/log
accesslog = "./access_log.txt"
errorlog = "./error_log.txt"
#errorlog = "-"
# Redirect stdout/stderr to log file
capture_output = False
# PID file so you can easily fetch process ID
pidfile = "./dev.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = True