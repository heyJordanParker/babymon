from admin.server import Server
import admin.supervisor as supervisor
from lib.quicklock import lock
from time import sleep

if __name__ == '__main__':
    lock()
    Server.startup()
    while True:
        supervisor.check()
        sleep(1)
