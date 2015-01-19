# This is where all the error objects are stored.

class ConnectionError(Exception):
    def __str__(self):
        return 'Cannot connect to MySQL. Please check your configuration file.'

class APICallError(Exception):
    def __str__(self):
        return 'Cannot connect to Qualtrics. Please check your configuration file.'
