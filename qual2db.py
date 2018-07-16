import cherrypy
import os
from qual2db.gui import Root

DIR = os.path.dirname(os.path.realpath(__file__))

qual_creds = {
    'baseurl':configurations['Qualtrics_Credentials']['baseurl'],
    'token':configurations['Qualtrics_Credentials']['Token']
    }

sql_creds = {
    'constr':configurations['MySQL_Credentials']['constr']
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
        Root(constr='sqlite:///testing.db'), config=config)
    cherrypy.quickstart(app, config=config)


if __name__ == "__main__":
    main()
