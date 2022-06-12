import configparser
import logsetup

from fungiforme.fungiforme import Fungiforme


def main():
    config = configparser.ConfigParser()
    config.read('fungiforme.ini', encoding='UTF-8')
    logsetup.setup(config)
    
    fungiforme = Fungiforme(config)
    fungiforme.load_extensions('fungiforme.extensions')
    fungiforme.run()


if __name__ == "__main__":
    main()
