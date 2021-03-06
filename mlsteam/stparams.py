import os
import yaml
import logging


## get value from HOME/lab/mlsteam.yml
def get_value(key, default=None):
    _dir = os.getenv('HOME', None)
    if not _dir:
        logging.warning("use default value for {}, HOME environment variable undefined.".format(key))
        return default
    param_file = os.path.join(_dir, "lab", "mlsteam.yml")
    if not os.path.exists(param_file):
        logging.warning("use default value for {}, mlsteam.yml not found.".format(key))
        return default
    params = {}
    with open(param_file, 'r') as f:
        params = yaml.safe_load(f)
    if "params" not in params:
        logging.warning("use default value for {}, undefined variable.".format(key))
        return default
    for k, v in params["params"].iteritems():
        if key == k:
            if type(params["params"][key]) == list:
                logging.warning("key {} is a list, use first value".format(key))
                return params["params"][key][0]
            logging.info("use {}: {}".format(k, v))
            return params["params"][key]
    logging.warning("use default value for {}, undefined variable.".format(key))
    return default
