from ConfigParser import ConfigParser, NoOptionError, NoSectionError
import pkg_resources
from os import path

own_dir = path.dirname(path.abspath(__file__))

############ READ CONFIG FILE #################

# Read defaults and override with user configs
defaults_file = pkg_resources.resource_filename(__name__, "default.ini")
configs_file = pkg_resources.resource_filename(__name__, "config.ini")
conf = ConfigParser()
conf.read(defaults_file)
conf.read(configs_file)

########## DEFINE A LOG FUNCTION ###############

def log(msg):
    global conf
    print(msg)
    try:
        log_file = conf.get("UNIT", "log_file")
        with open(log_file, 'a') as handle:
            handle.write(msg + "\n")
    except NoOptionError:
        pass
    except NoSectionError:
        pass
