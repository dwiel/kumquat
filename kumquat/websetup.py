"""Setup the kumquat application"""
import logging

from paste.deploy import appconfig
from pylons import config

from kumquat.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup kumquat here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
