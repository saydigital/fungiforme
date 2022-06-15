# Copyright 2022-TODAY Rapsodoo Italia S.r.L. (www.rapsodoo.com)
# # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

import configparser
import logsetup

from fungiforme.fungiforme import Fungiforme


def main():
    config = configparser.ConfigParser()
    config.read('fungiforme.ini', encoding='UTF-8')
    logsetup.setup(config)
    
    fungiforme = Fungiforme(config)
    fungiforme.load_extensions()
    fungiforme.run()


if __name__ == "__main__":
    main()
