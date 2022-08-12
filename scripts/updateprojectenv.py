# copied from: https://www.activestate.com/resources/quick-reads/how-to-update-all-python-packages/
from subprocess import call

import pkg_resources

for dist in pkg_resources.working_set:
    call("python -m pip install --upgrade " + dist.project_name, shell=True)
