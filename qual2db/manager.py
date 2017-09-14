import inspect
import sqlite3
import json
import time
import zipfile
import os
import configparser

import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from qual2db.datamodel import Base
from qual2db import datamodel

Session = sessionmaker()

# -----------------------------------------------------------------------
# Parse configuration
# -----------------------------------------------------------------------

package_directory = os.path.dirname(__file__)
config_file = os.path.join(package_directory, 'config.ini')

config = configparser.ConfigParser()
config.read(config_file)

download_directory = config['Basic']['download_directory']

qual_creds = {
    'baseurl': config['Qualtrics Credentials']['baseurl'],
    'token': config['Qualtrics Credentials']['Token']
}

sql_creds = {
    'constr': config['MySQL Credentials']['constr']
}

# -----------------------------------------------------------------------
# Key variables
# -----------------------------------------------------------------------

default_respondent_fields = [
    'ResponseID',
    'ResponseSet',
    'StartDate',
    'EndDate',
    'ExternalDataReference',
    'Finished',
    'IPAddress',
    'LocationAccuracy',
    'LocationLatitude',
    'LocationLongitude',
    'RecipientEmail',
    'RecipientFirstName',
    'RecipientLastName',
    'Status'
]

# -----------------------------------------------------------------------
# Mangement Classes
# -----------------------------------------------------------------------


class DatabaseInterface:

    def __init__(self, constr, Base):
        self.engine = create_engine(constr, pool_recycle=280)
        Base.metadata.create_all(self.engine)
        self.SessionMaker = scoped_session(sessionmaker(bind=self.engine))
        self.__session = None

        self.archetypes = dict()
        for name, obj in inspect.getmembers(datamodel):
            if inspect.isclass(obj):
                try:
                    self.archetypes[obj.__tablename__] = obj
                except:
                    continue

    def __getattr__(self, name):
        return getattr(self.__session, name)

    def close(self):
        try:
            self.__session.close()
        except:
            self.__session = None

    def connect(self):
        self.close()
        self.__session = self.SessionMaker()

    def bind_table(self, table_name):
        """Binds a database table to a function for retriving a pandas dataframe view of the database"""
        def get_table(interface=self, table=table_name, sql=None, obj=False):
            if obj:
                archetype = interface.archetypes[table_name]
                cols = archetype.__table__.columns.keys()
                data = interface.session.query(archetype).all()

                df = pd.DataFrame([[getattr(i, j) for j in cols] + [i]
                                   for i in data], columns=cols + ['obj'])
            else:
                df = pd.read_sql_table(table_name, self.engine)
                if sql:
                    df = df.query(sql)
            return df

        get_table.__name__ = table_name
        return get_table


class QualtricsInterface:
    """Interfaces with qualtrics.com via the API."""

    def __init__(self):
        pass

    def api_request(self, call='surveys', method='GET', parms=None, export=False, debug=False):
        """Makes a api request

        Parameters
        ----------
        call : the api call
        method : the api method
        parms : parameters required for the call
        export : signifies if this call is a data download/export
        debug : if True prints out log
        """

        url = qual_creds['baseurl'] + call

        headers = {
            'x-api-token': qual_creds['token'],
            'content-type': 'application/json'
        }

        if parms:
            parms = json.dumps(parms)

        response = requests.request(method, url, data=parms, headers=headers)

        if export:
            qid = call.replace('responseexports/', '').replace('/file', '')
            path = download_directory + qid + '_data'

            with open(path + '.zip', 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)

            zipfile.ZipFile(path + '.zip').extractall(path)
            return path

        try:
            data = response.json()
        except:
            return response.text

        return data['result']

    def listSurveys(self, debug=False):
        """Creates a list of surveys the API account has access to."""
        data = self.api_request(call='surveys', debug=debug)

        survey_list = []
        for survey in data['elements']:
            qid = survey['id']
            name = survey['name']
            active = survey['isActive']

            survey_list.append([qid, name, active])

        return survey_list

    def getSurvey(self, qid, debug=False):
        """Quickly creates a dictionary with basic details about a given survey."""
        schema = self.api_request(call='surveys/' + qid, debug=debug)
        return schema

    def getData(self, qid, last_response=None, debug=False):
        """Gets survey data."""

        parms = {
            "surveyId": qid,
            "format": "json"
        }

        if last_response:
            parms['lastResponseId'] = last_response

        print('Downloading data.')
        data = self.api_request(call='responseexports/',
                                method='POST', parms=parms, debug=debug)
        export_id = data['id']

        complete = 0
        while complete < 100:
            progress = self.api_request(
                call='responseexports/' + export_id, method='GET', debug=debug)
            complete = progress['percentComplete']
            print(complete)

        download_call = 'responseexports/' + export_id + '/file'
        download_path = self.api_request(
            call=download_call, method='GET', export=True, debug=debug)

        #data_file = download_path + '\\' + os.listdir(download_path)[0]
        data_file = os.path.join(download_path, os.listdir(download_path)[0])

        data = open(data_file, 'r')

        return json.load(data)['responses']


class SurveyManager(DatabaseInterface, QualtricsInterface):
    """Interface for working with sqlalchemy, sqlite3, and data classes"""

    def __init__(self, constr=sql_creds['constr'], Base=Base):
        DatabaseInterface.__init__(self, constr, Base)
        QualtricsInterface.__init__(self)

        for table in self.archetypes:
            func = self.bind_table(table)
            setattr(self, table, func)

    def add_survey(self, qid, replace=False):
        """Adds a survey to the database."""
        self.connect()

        existing = self.query(datamodel.Survey).filter(
            datamodel.Survey.qid == qid).first()

        if existing:
            if not replace:
                return existing
            else:
                self.delete(existing)

        schema = self.getSurvey(qid)
        data = self.getData(qid)

        survey = datamodel.Survey()
        schema_mapper(survey, schema)
        self.add(survey)
        self.commit()

        index = build_index(survey, schema)
        parse_responses(survey, schema, data)
        self.add(survey)
        self.commit()
        return survey

# -----------------------------------------------------------------------
# Data conversion functions
# -----------------------------------------------------------------------


def schema_mapper(Survey, schema):
    # map survey attributes
    schema_copy = schema.copy()
    data_mapper(Survey, schema_copy)

    Survey.blocks = entity_mapper(datamodel.Block, schema_copy['blocks'])
    block_map = map_blocks(schema_copy)
    block_index = Survey.get_blocks()

    Survey.questions = entity_mapper(
        datamodel.Question, schema_copy['questions'])

    # add the choices and subquestions to each question
    for question in Survey.questions:
        # question.parse_question_text()
        data = schema_copy['questions'][question.qid]

        try:
            question.subquestions = entity_mapper(
                datamodel.SubQuestion, data['subQuestions'])
        except:
            pass

        try:
            question.choices = entity_mapper(datamodel.Choice, data['choices'])
        except:
            pass

        # add to block
        related_block = block_map[question.qid]
        block_index[related_block].questions.append(question)

    return Survey


def data_mapper(instance, dictionary, skip_keys=['choices', 'subQuestions'], qid=None):
    dictionary_copy = dictionary.copy()

    try:
        dictionary_copy['qid'] = dictionary_copy.pop('id')
    except:
        dictionary_copy['qid'] = str(qid)

    drop_keys = []

    # find fields with subfields and parse them out
    for key in dictionary_copy.keys():

        if key in skip_keys:
            drop_keys.append(key)
            continue

        if isinstance(dictionary_copy[key], dict):
            for sub_key in dictionary_copy[key].keys():
                if hasattr(instance, sub_key):
                    setattr(instance, sub_key, dictionary_copy[key][sub_key])
            drop_keys.append(key)

        if isinstance(dictionary_copy[key], list):
            if hasattr(instance, key):
                setattr(instance, key, len(dictionary_copy[key]))
            drop_keys.append(key)

    # drop keys with subfields or lists
    for drop_key in drop_keys:
        dictionary_copy.pop(drop_key)

    # find the rest of the fields
    for key in dictionary_copy.keys():
        if hasattr(instance, key):
            setattr(instance, key, dictionary_copy[key])

    return instance


def entity_mapper(Entity, entity_data, skip_keys=None):
    entity_list = []
    for entity in entity_data:
        i = Entity()
        try:
            data = entity_data[entity]
        except:
            data = entity
        if skip_keys:
            data_mapper(i, data, skip_keys, qid=entity)
        else:
            data_mapper(i, data, qid=entity)
        entity_list.append(i)
    return entity_list


def map_blocks(schema):
    block_data = schema['blocks'].copy()
    block_map = dict()
    for block in block_data:
        elements = block_data[block]['elements']
        for element in elements:
            if element['type'] == 'Question':
                block_map[element['questionId']] = block
    return block_map


def build_index(Survey, schema):
    index = dict()
    index['exportColumnMap'] = schema['exportColumnMap'].copy()
    index['questions'] = Survey.get_questions()
    index['subquestions'] = Survey.get_subquestions()
    index['choices'] = Survey.get_choices()
    index['embedded_data'] = Survey.get_embedded_data()
    return index


def parse_response(index, column, entry):
    response = datamodel.Response()

    # column is a respondnet field
    if column in default_respondent_fields:
        return False

    # column is embedded data
    if column in index['embedded_data']:
        response.embedded_data_id = embedded_data_id = index[
            'embedded_data'][column].id
        response.textEntry = entry
        return response

    question_qid = index['exportColumnMap'][column]['question']
    question_id = index['questions'][question_qid].id
    question_type = index['questions'][question_qid].type
    response.question_id = question_id

    try:
        subquestion_qid = index['exportColumnMap'][
            column]['subQuestion'].split('.')[-1]
        subquestion_id = index['subquestions'][
            question_qid][int(subquestion_qid)].id
        response.subquestion_id = subquestion_id
    except:
        pass

    try:
        choice_qid = index['exportColumnMap'][column]['choice'].split('.')[-1]
        choice_id = index['choices'][question_qid][int(choice_qid)].id
        response.choice_id = choice_id
    except:
        pass

    if 'TEXT' in column:
        response.textEntry = entry
    elif question_type == 'TE':
        response.textEntry = entry
    else:
        try:
            response.choice_id = index['choices'][question_qid][int(entry)].id
        except:
            response.choice_id = entry

    return response


def parse_responses(Survey, schema, data):
    index = build_index(Survey, schema)

    for responses in data:
        respondent = data_mapper(datamodel.Respondent(), responses)

        for record in responses:
            response = parse_response(index, record, responses[record])
            if response:
                respondent.responses.append(response)

        Survey.respondents.append(respondent)

    return Survey
