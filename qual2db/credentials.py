'''

credentials.py

'''

import os
import configparser

package_directory = os.path.dirname(__file__)
config_file = os.path.join(package_directory, 'config.ini')

config = configparser.ConfigParser()
config.read(config_file)

download_directory = config['Basic']['download_directory']

qualtrics_credentials = {
	'baseurl': config['Qualtrics Credentials']['baseurl'],
	'user' : config['Qualtrics Credentials']['User'],
	'password' : config['Qualtrics Credentials']['Password'],
	'token' : config['Qualtrics Credentials']['Token'],
	'version' : config['Qualtrics Credentials']['Version']
}

sql_credentials = {

	'user': config['MySQL Credentials']['sqlUser'],
	'password': config['MySQL Credentials']['sqlPassword'],
	'host': config['MySQL Credentials']['sqlHost'],
	'db': config['MySQL Credentials']['sqlDB']
}


