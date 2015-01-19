## This parses the configuration file.

import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.ini')

baseurl = config.get('Qualtrics Credentials','baseurl')
User = config.get('Qualtrics Credentials','User')
Password = config.get('Qualtrics Credentials','Password')
Token = config.get('Qualtrics Credentials','Token')
Version = config.get('Qualtrics Credentials','Version')

sqlUser = config.get('MySQL Credentials','sqlUser')
sqlPassword = config.get('MySQL Credentials','sqlPassword')
sqlHost = config.get('MySQL Credentials','sqlHost')
sqlDB = config.get('MySQL Credentials','sqlDB')
