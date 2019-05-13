import os
import yaml


## get value from JOB_DIR/param.yml
def get_value(key):
    _dir = os.getenv('JOB_DIR', None)
    if not _dir:
        raise ValueError("Environment error")
    param_file = os.path.join(_dir, "param.yml")
    if not os.path.exists(param_file):
        raise ValueError("Parameters undefined")
    params = {}
    with open(param_file, 'r') as f:
        params = yaml.safe_load(f)
    for k, v in params.iteritems():
        if key == k:
            return params[key]
    raise ValueError("Can not find '{}' from get_value()".format(key))
