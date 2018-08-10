#!/usr/bin/env python
# This is a generic launcher for flaskit application
# Could be use as a WSGI entry point
# or directly call from the command line (with a builtin web sevrer) for testing
# Environnement has to be identified (that point to configurations files) :
#  - in WSGI context : this is the WSGIProcessGroup (automatic identification)
#  - in direct context : could be pass as an arg on command line (there is a default value)
#
# 2015/04 L.Licour
#

import os
import sys
import optparse
import traceback


def configure(dir_base, env):

    # add projet dir in path
    sys.path.insert(0, dir_base)

    # activate local virtualenv (if defined)
    activate_this = dir_base + '/venv/bin/activate_this.py'
    if os.path.exists(activate_this):
        execfile(activate_this, dict(__file__=activate_this))

    # Read config file from application
    config = {}
    filename = "%s/env/%s/%s" % (dir_base, env, "config.cfg")
    try:
        with open(filename) as config_file:
            for line in config_file:
                line = line.strip()
                # skip blank lines and comments
                if len(line) == 0 or line[0] == "#":
                    continue
                (key, val) = line.split("=", 1)
                config[key.strip()] = val.strip().strip('"')
    except IOError as e:
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise Exception(e)

    return config


if __name__ == '__main__':

    # direct execution with builtin webserver (dev mode)
    project_dir = '.'
    env = 'vga-api.default'
    config = configure(project_dir, env)

    from flaskit import app as application
    application.init(project_dir, env, api_name=config["API_NAME"])

else:

    # This is a WSGI context
    import mod_wsgi

    # Get process group defined in wsgi to identify current env
    env = mod_wsgi.process_group
    project_dir = os.path.dirname(os.path.realpath("%s/../.." % __file__))
    config = configure(project_dir, env)

    # start application
    try:
        from flaskit import app as application
        application.init(project_dir, env, api_name=config["API_NAME"])
    except Exception:
        print traceback.format_exc()