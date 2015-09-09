##### Credential Parser ########
################################

# This script parses credentials from the config.ini file

import os
import ConfigParser

package_directory = os.path.dirname(__file__)
config_file = os.path.join(package_directory, 'config.ini')

config = ConfigParser.ConfigParser()
config.read(config_file)

baseurl = config.get('Qualtrics Credentials','baseurl')
User = config.get('Qualtrics Credentials','User')
Password = config.get('Qualtrics Credentials','Password')
Token = config.get('Qualtrics Credentials','Token')
Version = config.get('Qualtrics Credentials','Version')

sqlUser = config.get('MySQL Credentials','sqlUser')
sqlPassword = config.get('MySQL Credentials','sqlPassword')
sqlHost = config.get('MySQL Credentials','sqlHost')
sqlDB = config.get('MySQL Credentials','sqlDB')

