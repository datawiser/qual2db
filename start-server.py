import sys
sys.path.append('C://Users/Owen/Documents/Projects/qual2db')

import cherrypy
from qual2db.server import Root


def main():

    config = {
        '/': {
            'tools.sessions.on': True
        },

        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'C:/Users/Owen/Documents/Projects/coder/txtcoder/static'

        }
    }

    # Create, configure and start application
    app = cherrypy.Application(
        Root(constr='sqlite:///testing.db'), config=config)
    cherrypy.quickstart(app, config=config)


if __name__ == "__main__":
    main()
