# Imports 
import sys
from os import environ
from subprocess import run

# script
environ["FLASK_APP"] = "src/__init__.py"
environ["FLASK_DEBUG"] = "1"

if sys.argv[1].lower() == 'run':
    sys.exit(run(["python", "-m", "flask", "run", "--cert=scripts/cert.pem", "--key=scripts/key.pem"]))
    
else:
    sys.exit(0)