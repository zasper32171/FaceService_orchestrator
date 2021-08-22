import time
import sys

from config import ConfigReader


def usage():

    print('Usage: python3 main.py ')


def error():

    usage()
    exit()


def main():

    if len(sys.argv) != 2:
        error()

    conf = ConfigReader(sys.argv[1])
    coordinator = conf.init_coordinator()

    try:
        coordinator.start()

        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:

        coordinator.stop()


if __name__ == '__main__':

    main()
