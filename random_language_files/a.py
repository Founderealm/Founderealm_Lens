import os
from pathlib import Path
from shared import shared_value


class Alpha:
    def run(self):
        return os.getcwd() + str(Path(".")) + shared_value()


def helper(x):
    return Alpha().run()
