import inspect
import sqlite3

import json
import time
import zipfile
import os

import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qual2db.datamodel import Base
from qual2db import datamodel

from qual2db.datamodel import Survey, Block, Question, SubQuestion, Choice
from qual2db.datamodel import Respondent, Response, default_respondent_fields

import requests

from qual2db.credentials import qualtrics_credentials as q_creds
from qual2db.credentials import download_directory

Session = sessionmaker()


class DatabaseInterface:

    def __init__(self, path):
        global Base

        # add db extension if unspecified
        if path[:-3] != '.db':
            path += '.db'

        Session = sessionmaker()
        self.path = path

        self.engine = create_engine(
            'sqlite+pysqlite:///' + self.path, module=sqlite3.dbapi2, echo=False)

        Session.configure(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

        self.connection = sqlite3.connect(self.path)

        self.archetypes = dict()
        for name, obj in inspect.getmembers(datamodel):
            if inspect.isclass(obj):
                try:
                    self.archetypes[obj.__tablename__] = obj
                except:
                    continue

    def save(self, Objects):
        """Saves objects to the database. Takes a list of a single object."""
        if isinstance(Objects, list):
            self.session.add_all(Objects)
        else:
            self.session.add(Objects)
        self.session.commit()

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

        url = q_creds['baseurl'] + call

        headers = {
            'x-api-token': q_creds['token'],
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

        data_file = download_path + '\\' + os.listdir(download_path)[0]
        data = open(data_file, 'r')

        return json.load(data)['responses']


class Manager(DatabaseInterface, QualtricsInterface):
    """Interface for working with sqlalchemy, sqlite3, and data classes"""

    def __init__(self, path):
        DatabaseInterface.__init__(self, path)
        QualtricsInterface.__init__(self)

        for table in self.archetypes:
            func = self.bind_table(table)
            setattr(self, table, func)


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


def schema_mapper(Survey, schema):
    # map survey attributes
    schema_copy = schema.copy()
    data_mapper(Survey, schema_copy)

    Survey.blocks = entity_mapper(Block, schema_copy['blocks'])
    block_map = map_blocks(schema_copy)
    block_index = Survey.get_blocks()

    Survey.questions = entity_mapper(Question, schema_copy['questions'])

    # add the choices and subquestions to each question
    for question in Survey.questions:
        question.parse_question_text()
        data = schema_copy['questions'][question.qid]

        try:
            question.subquestions = entity_mapper(
                SubQuestion, data['subQuestions'])
        except:
            pass

        try:
            question.choices = entity_mapper(Choice, data['choices'])
        except:
            pass

        # add to block
        related_block = block_map[question.qid]
        block_index[related_block].questions.append(question)

    return Survey


def build_index(Survey, schema):
    index = dict()

    index['exportColumnMap'] = schema['exportColumnMap'].copy()
    index['questions'] = Survey.get_questions()
    index['subquestions'] = Survey.get_subquestions()
    index['choices'] = Survey.get_choices()
    index['embedded_data'] = Survey.get_embedded_data()

    return index


def parse_response(index, column, entry):
    response = Response()

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
        respondent = data_mapper(Respondent(), responses)

        for record in responses:
            response = parse_response(index, record, responses[record])
            if response:
                respondent.responses.append(response)

        Survey.respondents.append(respondent)

    return Survey
