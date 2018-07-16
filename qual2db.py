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

    # Create, configure and start application
    app = cherrypy.Application(
        Root(constr='sqlite:///testing.db'), config=config)
    cherrypy.quickstart(app, config=config)


if __name__ == "__main__":
    main()
