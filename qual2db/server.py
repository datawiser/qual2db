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
    def index(self):
        self.sm.connect()

        surveys = self.sm.listSurveys()
        surveys_in_db = self.sm.survey().qid.tolist()

        survey_row = Template(filename=os.path.join(
            DIR, 'templates/survey_row.html'))

        page = Template(filename=os.path.join(
            DIR, 'templates/login.html'))

        rows = ''

        for s in surveys:
            if s[0] in surveys_in_db:
                checked = 'checked'
                survey = self.sm.query(Survey).filter(Survey.qid == s[0]).one()
                qid = s[0]
                name = survey.name
                responses = str(len(survey.respondents))
                active = survey.isActive
                if active == '1':
                    active = True
                elif active == '0':
                    return False
                else:
                    pass
            else:
                checked = ''
                survey = self.sm.getSurvey(s[0])
                qid = s[0]
                name = survey['name']
                responses = survey['responseCounts']['auditable']
                active = survey['isActive']

            rows += survey_row.render(qid=qid, name=name,
                                      responses=responses, active=active, checked=checked)

        self.sm.close()
        return page.render(rows=rows)

    @cherrypy.expose
    def update(self, **qids):
        surveys_in_db = self.sm.survey().qid.tolist()
        if qids:
            for qid in qids:
                if qid in surveys_in_db:
                    pass
                else:
                    self.sm.add_survey(qid)
            for qid in surveys_in_db:
                if qid in qids:
                    pass
                else:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()
        else:
            for qid in surveys_in_db:
                if qid in qids:
                    pass
                else:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()

        raise cherrypy.InternalRedirect('index')

    @cherrypy.expose
    def home(self, username):
        return username
