import os
from pathlib import Path
class Alpha:
    def run(self):
        return os.getcwd() + str(Path("."))
def helper(x):
    return Alpha().run()
