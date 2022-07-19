import warnings

from logger import get_logger

warnings.filterwarnings("ignore", category=DeprecationWarning)
LOGGER = get_logger()


def main():
    print('Hello World!')
    LOGGER.info('Hello World! Welcome to Japan.')


if __name__ == "__main__":
    main()
