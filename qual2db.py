import cherrypy
import os
from qual2db.gui import Root
import configparser

DIR = os.path.dirname(os.path.realpath(__file__))
package_directory = os.path.dirname(__file__)
config_file = os.path.join(package_directory, 'qual2db', 'config.ini')

configurations = configparser.ConfigParser()
configurations.read(config_file)

qual_creds = {
    'baseurl':configurations['Qualtrics_Credentials']['baseurl'],
    'token':configurations['Qualtrics_Credentials']['Token']
    }

sql_creds = {
    'constr':configurations['SQL_Credentials']['constr']
    }

def main():

    config = {
        '/': {
            'tools.sessions.on': True
        },

        '/static': {
            'tools.staticdir.root': DIR,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'qual2db/static/'

        }
    }

    # Create, configure and start application
    app = cherrypy.Application(
        Root(constr=sql_creds['constr']), config=config)
    cherrypy.quickstart(app, config=config)


if __name__ == "__main__":
    main()
