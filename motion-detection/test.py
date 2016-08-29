from lib import config
from time import sleep
from lib.quicklock import lock


if __name__ == '__main__':
    lock()
    count = 800
    while count > 0:

        sleep(1)
        count -= 1
