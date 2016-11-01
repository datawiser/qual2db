'''

survey.py

'''

import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .datamodel import Base

from .datamodel import Survey, Block, Question, SubQuestion, Choice
from .datamodel import Respondent, Response, default_respondent_fields

Session = sessionmaker()

class Database(object):
    '''
    An interface for working with sqlalchemy, sqlite3, and data classes
    
    '''

    def __init__(self,name):
        '''
        '''
        global Session
        global Base

        # add db extension if unspecified
        if name[:-3]!='.db':
            name+='.db'
        
        self.name = name
        self.engine = create_engine('sqlite+pysqlite:///'+self.name, module=sqlite3.dbapi2,echo=False)
        
        Session.configure(bind=self.engine)
        self.session = Session()

        Base.metadata.create_all(self.engine)


    def survey(self,id=None,name=None):

        if id:
            query = self.session.query(Survey).filter_by(id=id)
            return query.first()

        else:
            return None


    def save(self,Entities):
        '''
        add changed or new entities to a project

        '''

        if isinstance(Entities, list):
            self.session.add_all(Entities)
        else:
            self.session.add(Entities)

        self.session.commit()


def data_mapper(instance,dictionary,skip_keys=['choices','subQuestions'],qid=None):
    '''
    This function maps a JSON object to a SQL object.
    '''

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

        if isinstance(dictionary_copy[key],dict):
            for sub_key in dictionary_copy[key].keys():
                if hasattr(instance, sub_key):
                    setattr(instance, sub_key, dictionary_copy[key][sub_key])
            drop_keys.append(key)

        if isinstance(dictionary_copy[key],list):
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

def entity_mapper(Entity,entity_data,skip_keys=None):
    '''
    '''
    entity_list = []
    for entity in entity_data:
        i = Entity()

        try:
            data = entity_data[entity]
        except:
            data = entity

        if skip_keys:
            data_mapper(i,data,skip_keys, qid=entity)
        else:
            data_mapper(i,data,qid=entity)
        
        entity_list.append(i)

    return entity_list

def map_blocks(schema):
    '''
    '''
    block_data = schema['blocks'].copy()

    block_map = dict()

    for block in block_data:
        elements = block_data[block]['elements']
        for element in elements:
            if element['type'] == 'Question':
                block_map[element['questionId']] = block

    return block_map

def schema_mapper(Survey,schema):
    '''
    takes a survey and maps it to a datamodel
    '''
    # map survey attributes
    schema_copy = schema.copy()
    data_mapper(Survey,schema_copy)

    Survey.blocks = entity_mapper(Block,schema_copy['blocks'])
    block_map = map_blocks(schema_copy)
    block_index = Survey.get_blocks()

    Survey.questions = entity_mapper(Question,schema_copy['questions'])

    # add the choices and subquestions to each question
    for question in Survey.questions:
        data = schema_copy['questions'][question.qid]
        
        try:
            question.subquestions = entity_mapper(SubQuestion,data['subQuestions'])
        except:
            pass

        try:
            question.choices = entity_mapper(Choice,data['choices'])
        except:
            pass

        # add to block
        related_block = block_map[question.qid]
        block_index[related_block].questions.append(question)

    return Survey


def build_index(Survey,schema):
    '''
    '''
    index = dict()

    index['exportColumnMap'] = schema['exportColumnMap'].copy()
    index['questions'] = Survey.get_questions()
    index['subquestions'] = Survey.get_subquestions()
    index['choices'] = Survey.get_choices()
    index['embedded_data'] = Survey.get_embedded_data()

    return index


def parse_response(index,column,entry):
    '''
    '''
    response = Response()

    # column is a respondnet field
    if column in default_respondent_fields:
        return False

    # column is embedded data
    if column in index['embedded_data']:
        response.embedded_data_id = embedded_data_id = index['embedded_data'][column].id
        response.textEntry = entry
        return False

    question_qid = index['exportColumnMap'][column]['question']
    question_id = index['questions'][question_qid].id
    response.question_id = question_id

    try:
        subquestion_qid = index['exportColumnMap'][column]['subQuestion'].split('.')[-1]
        subquestion_id = index['subquestions'][question_qid][int(subquestion_qid)].id
        response.subquestion_id = subquestion_id
    except:
        pass

    if 'TEXT' in column:
        response.textEntry = entry
    else:
        try:
            response.choice_id = int(entry)
        except:
            response.choice_id = entry
    
    return response

def parse_responses(Survey,schema,data):
    '''
    '''
    index = build_index(Survey,schema)

    for responses in data:
        respondent = data_mapper(Respondent(),responses)

        for record in responses:
            response = parse_response(index,record,responses[record])
            if response:
                respondent.responses.append(response)

        Survey.respondents.append(respondent)

    return Survey














