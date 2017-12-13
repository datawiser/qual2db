import cherrypy
import os
from qual2db.gui import Root

DIR = os.path.dirname(os.path.realpath(__file__))


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
	
	package_directory = os.path.dirname(__file__)
	config_file = os.path.join(package_directory, 'config.ini')

	config = configparser.ConfigParser()
	config.read(config_file)
	
	sql_creds = {
		'constr': config['MySQL Credentials']['constr']
	}

    app = cherrypy.Application(
        Root(constr=sql_creds['constr']), config=config)
    cherrypy.quickstart(app, config=config)


if __name__ == "__main__":
    main()
