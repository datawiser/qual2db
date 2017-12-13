import os

import cherrypy
import json
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

        page = Template(filename=os.path.join(
            DIR, 'templates/index.html'))

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
                    pass
                else:
                    self.sm.add_survey(qid)
            for qid in self.surveys_in_db:
                if qid in qids:
                    pass
                else:
                    self.sm.add_survey(qid)
                    #s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    #self.sm.delete(s)
                    #self.sm.commit()
        else:
            for qid in self.surveys_in_db:
                if qid in qids:
                    pass
                else:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()

        self.surveys_in_db = self.sm.survey().qid.tolist()
        return True
        # cherrypy.InternalRedirect('index')
    
    #Schema
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addQualtricsSurveySchema(self):
        qids = cherrypy.request.json
        self.surveys_in_db = self.sm.survey().qid.tolist()
        if qids:
            for num in qids:
                qid = qids[num]
                if qid in self.surveys_in_db:
                    pass
                else:
                    self.sm.add_survey(qid)
            for qid in self.surveys_in_db:
                if qid in qids:
                    pass
                else:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()
        else:
            for qid in self.surveys_in_db:
                if qid in qids:
                    pass
                else:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()
                    
        self.surveys_in_db = self.sm.survey().qid.tolist()
        raise cherrypy.InternalRedirect('index')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def addQualtricsSurveyData(self):
        qids = cherrypy.request.json
        self.surveys_in_db = self.sm.survey().qid.tolist()
        if qids:
            for num in qids:
                qid = qids[num]
                if qid in self.surveys_in_db:
                    pass
                else:
                    self.sm.add_survey(qid)
            for qid in self.surveys_in_db:
                if qid in qids:
                    pass
                else:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()
        else:
            for qid in self.surveys_in_db:
                if qid in qids:
                    pass
                else:
                    s = self.sm.query(Survey).filter(Survey.qid == qid).one()
                    self.sm.delete(s)
                    self.sm.commit()
                    
        self.surveys_in_db = self.sm.survey().qid.tolist()
        raise cherrypy.InternalRedirect('index')
    
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
        else:
            pass
        
        self.surveys_in_db = self.sm.survey().qid.tolist()
        return True
        #raise cherrypy.InternalRedirect('index')
    
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
            aQualSurvey['Responses'] = survey['responseCounts']['auditable']
            aQualSurvey['Active'] = survey['isActive']
            if s[0] in self.surveys_in_db:
                aQualSurvey['Indatabase'] = True
            else:
                aQualSurvey['Indatabase'] = False
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
            checked = 'checked'
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
            sqlSurveys.append(aSQLSurvey)

        self.sm.close()
        return sqlSurveys