from src.main import app
from os import chdir
from os.path import abspath, join

if __name__ == '__main__':
    # Activates website
    try:
        print("[CHANGING DIR] Wrong directory, changing to the correct directory...")
        chdir(join(abspath('.'), 'src'))
        print("[CHANGING DIR] Directory change successful!")
        print("[CONNECTING] Connecting to website...")
        app.run(debug=True)
    except Exception:
        print("[CONNECTING] Connecting to website...")
        app.run(debug=True)