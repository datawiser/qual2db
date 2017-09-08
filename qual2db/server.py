import os
import random
import math
import pickle
from collections import defaultdict

import pandas as pd

import cherrypy
from mako.template import Template

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import String, Integer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from qual2db.datamodel import Survey, Base
from qual2db.manager import SurveyManager

DIR = os.path.dirname(__file__)


class Root(object):

    def __init__(self, constr):
        self.sm = SurveyManager(constr, Base)

    # for testing purposes
    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()

    @cherrypy.expose
    def login(self):
        self.sm.connect()
        surveys = self.sm.listSurveys()
        table = '<h3>Surveys in Qualtrics</h3>'
        table += '<table><th>qid</th><th>name</th><th>active</th>'
        for survey in surveys:
            table += '<tr>'
            for cell in survey:
                table += '<td>' + str(cell) + '</td>'
            table += '</tr>'
        table += '</table>'

        #page = Template(filename=os.path.join(DIR, 'templates/login.html'))
        return table

    @cherrypy.expose
    def home(self, username):
        return username
