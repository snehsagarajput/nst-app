#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Ngrok Tunneling which exposes local servers behind NATs
and firewalls to the public internet over secure tunnels.
'''

#######################################################################
#                                                                     #
#                *** CREDITS TO THE ORIGINAL AUTHOR ***               #
#   https://github.com/gstaff/flask-ngrok/blob/master/flask_ngrok.py  #
#                                                                     #
#######################################################################

__author__ = 'Sneh Sagar'
__copyright__ = None
__credits__ = ['Sneh Sagar']
__license__ = 'GPL'
__version__ = '1.0.1'
__email__ = 'snehsagarajput@gmail.com'
__status__ = 'Production'






import atexit
import json
import os
import platform
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path
from threading import Timer
import webbrowser

import requests


def _get_command():
    system = platform.system()
    if system == "Darwin":
        command = "ngrok"
    elif system == "Windows":
        command = "ngrok.exe"
    elif system == "Linux":
        command = "ngrok"
    else:
        raise Exception("{system} is not supported".format(system=system))
    return command


def _run_ngrok(port):
    command = _get_command()
    ngrok_path = str(Path(tempfile.gettempdir(), "ngrok"))
    _download_ngrok(ngrok_path)
    executable = str(Path(ngrok_path, command))
    os.chmod(executable, 0o777)
    ngrok = subprocess.Popen([executable, 'http', str(port)])
    atexit.register(ngrok.terminate)
    localhost_url = "http://localhost:4040/api/tunnels"  # Url with tunnel details
    time.sleep(1)
    tunnel_url = requests.get(localhost_url).text  # Get the tunnel information
    j = json.loads(tunnel_url)

    tunnel_url = j['tunnels'][0]['public_url']  # Do the parsing of the get
    tunnel_url = tunnel_url.replace("https", "http")
    return tunnel_url


def _download_ngrok(ngrok_path):
    if Path(ngrok_path).exists():
        return
    system = platform.system()
    if system == "Darwin":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip"
    elif system == "Windows":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip"
    elif system == "Linux":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"
    else:
        raise Exception(f"{system} is not supported")
    download_path = _download_file(url)
    with zipfile.ZipFile(download_path, "r") as zip_ref:
        zip_ref.extractall(ngrok_path)


def _download_file(url):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    download_path = str(Path(tempfile.gettempdir(), local_filename))
    with open(download_path, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    return download_path


def start_ngrok(port):
    ngrok_address = _run_ngrok(port)
    print(" *\033[92m Running on "+str(ngrok_address)+" \033[0m")
    print("\033[1m Click the above BLUE URL to open webpage :) \033[0m")


def run_with_ngrok(app):
    """
    The provided Flask app will be securely exposed to the public internet via ngrok when run,
    and the its ngrok address will be printed to stdout
    :param app: a Flask application object
    :return: None
    """
    old_run = app.run

    def new_run(*args, **kwargs):
        thread = Timer(1, start_ngrok, args=(5000,))
        thread.setDaemon(True)
        thread.start()
        old_run(*args, **kwargs)
    app.run = new_run
