import os
import random
import math
import pickle
import json
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
        self.surveys_in_db = self.sm.survey().qid.tolist()

    # for testing purposes
    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()

    @cherrypy.expose
    def index(self):

        page = Template(filename=os.path.join(DIR, 'templates/index.html'))

        return page.render()

    #Sync All
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def qualtricsSyncAll(self):
        qids = cherrypy.request.json
        if qids:
            for num in qids:
                qid = qids[num]
                if qid in self.surveys_in_db:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()
                self.sm.add_survey(qid)
        self.surveys_in_db = self.sm.survey().qid.tolist()
        return True
    
    #Schema
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addQualtricsSurveySchema(self):
        qids = cherrypy.request.json
        if qids:
            for num in qids:
                qid = qids[num]
                if qid in self.surveys_in_db:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()
                self.sm.add_schema(qid)
        self.surveys_in_db = self.sm.survey().qid.tolist()
        return True

    #Data
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addQualtricsSurveyData(self):
        qids = cherrypy.request.json
        if qids:
            for num in qids:
                qid = qids[num]
                if qid in self.surveys_in_db:
                    self.sm.delete_data(qid)
                    self.sm.add_data(qid)
        self.surveys_in_db = self.sm.survey().qid.tolist()
        return True
    
    #Remove
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def removeSqlSurvey(self):
        qids = cherrypy.request.json
        if qids:
            for num in qids:
                qid = qids[num]
                if qid in self.surveys_in_db:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()
        self.surveys_in_db = self.sm.survey().qid.tolist()
        return True
        
    #Clear
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def clearSqlSurveyData(self):
        qids = cherrypy.request.json
        if qids:
            for num in qids:
                qid = qids[num]
                if qid in self.surveys_in_db:
                    self.sm.delete_data(qid)
        self.surveys_in_db = self.sm.survey().qid.tolist()
        return True
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def qualtricsSurveys(self, **kwargs):
        self.sm.connect()

        surveys = self.sm.listSurveys()

        qualtricsSurveys = []

        for s in surveys:
            aQualSurvey = {}
            survey = self.sm.getSurvey(s[0])
            aQualSurvey['Name'] = survey['name']
            aQualSurvey['Qid'] = s[0]

            if 'responseCounts' in survey:
                aQualSurvey['Responses'] = (survey['responseCounts']['generated'] + survey['responseCounts']['auditable'] - survey['responseCounts']['deleted'])
            else:
                pass

            aQualSurvey['Active'] = survey['isActive']

            if s[0] in self.surveys_in_db:
                aQualSurvey['Indatabase'] = True
            else:
                aQualSurvey['Indatabase'] = False

            aQualSurvey['lastmodified'] = survey['lastModifiedDate']
            qualtricsSurveys.append(aQualSurvey)
        self.sm.close()
        return qualtricsSurveys
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sqlSurveys(self, **kwargs):
        self.sm.connect()

        sqlSurveys = []

        for sq in self.surveys_in_db:
            aSQLSurvey = {}
            survey = self.sm.query(Survey).filter(Survey.qid == sq).one()
            aSQLSurvey['Qid'] = sq
            aSQLSurvey['Name'] = survey.name
            aSQLSurvey['Responses'] = str(len(survey.respondents))
            active = survey.isActive
            if active == '1':
                aSQLSurvey['Active'] = True
            elif active == '0':
                aSQLSurvey['Active'] = False
            else:
                pass
            aSQLSurvey['Indatabase'] = True
            aSQLSurvey['lastmodified'] = survey.lastModifiedDate
            sqlSurveys.append(aSQLSurvey)
        self.sm.close()
        return sqlSurveys

#class Root(object):

#    def __init__(self, constr):
#        self.sm = SurveyManager(constr, Base)
#        self.surveys_in_db = self.sm.survey().qid.tolist()

#    # for testing purposes
#    @cherrypy.expose
#    def shutdown(self):
#        cherrypy.engine.exit()

#    @cherrypy.expose
#    def get_databases(self,checkbox1):
#        databases = []
#        databases = checkbox1
#        return databases

#    @cherrypy.expose
#    def index(self):
#        print('gui-index')
#        self.sm.connect()

#        surveys = self.sm.listSurveys()
 
#        surveys_in_db = self.sm.survey().qid.tolist()

#        survey_row = Template(filename=os.path.join(DIR, 'templates/survey_row.html'))

#        page = Template(filename=os.path.join(DIR, 'templates/login.html'))

#        in_db_rows = '' 
#        not_in_db_rows = ''
#        rows = ''


#        for s in surveys:
#            survey = self.sm.getSurvey(s[0])
#            qid = s[0]
#            name = survey['name']
#            questions = str(len(survey['questions'])) 
#            active = survey['isActive']

#            if  'responseCounts' in survey:
#                responses = survey['responseCounts']['auditable']
#            else:
#                pass

#            size=int(questions)*int(responses)

#            if s[0] in surveys_in_db:
#                checked = 'checked'
#                in_db_rows += survey_row.render(qid=qid, name=name, responses=responses, active=active, size=size, checked=checked)
#            else:
#                checked = ''
#                not_in_db_rows += survey_row.render(qid=qid, name=name, responses=responses, active=active, size=size, checked=checked)

#        rows += survey_row.render(qid=qid, name=name, responses=responses, active=active, size=size, checked=checked)

#        self.sm.close()
#        return page.render(rows=rows, in_db_rows = in_db_rows, not_in_db_rows = not_in_db_rows)          


#    @cherrypy.expose
#    def update(self, **qids):
#        print('gui-update')
        
#        surveys = self.sm.listSurveys()
#        surveys_in_db = self.sm.survey().qid.tolist()

#        if qids:
#            for qid in qids:
#                if qid in surveys_in_db:
#                    pass
#                else:
#                    for s in surveys:
#                        if qid == s[0]:
#                            survey = self.sm.getSurvey(s[0])
#                            print(survey['name'])
#                    self.sm.add_survey(qid)
#            for qid in surveys_in_db:
#                if qid in qids:
#                    pass
#                else:
#                    print("b")
#                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
#                    self.sm.delete(s)
#                    self.sm.commit()
#        else:
#            for qid in surveys_in_db:
#                if qid in qids:
#                    pass
#                else:
#                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
#                    self.sm.delete(s)
#                    self.sm.commit()
        
#        raise cherrypy.InternalRedirect('index')

#    #Sync All
#    @cherrypy.expose
#    @cherrypy.tools.json_out()
#    @cherrypy.tools.json_in()
#    def qualtricsSyncAll(self):
#        qids = cherrypy.request.json
#        if qids:
#            for num in qids:
#                qid = qids[num]
#                if qid in self.surveys_in_db:
#                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
#                    self.sm.delete(s)
#                    self.sm.commit()
#                self.sm.add_survey(qid)
#        self.surveys_in_db = self.sm.survey().qid.tolist()
#        return True

#    @cherrypy.expose
#    def home(self, username):
#        print('gui-home')
#        return username
