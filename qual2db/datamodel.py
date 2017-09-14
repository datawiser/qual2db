"""
datamodel.py
"""
from bs4 import BeautifulSoup

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Numeric, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# create the declarative base
Base = declarative_base()


class Survey(Base):
    __tablename__ = 'survey'

    id = Column(Integer, primary_key=True)
    qid = Column(String(length=50))
    name = Column(String(length=50))  # , unique=True)

    isActive = Column(String(length=50))
    creationDate = Column(String(length=50))
    lastModifiedDate = Column(String(length=50))
    ownerId = Column(String(length=50))
    organizationId = Column(String(length=50))

    auditable = Column(Integer)
    deleted = Column(Integer)
    generated = Column(Integer)

    endDate = Column(String(length=50))
    startDate = Column(String(length=50))

    def get_blocks(self):
        blocks = dict()
        for block in self.blocks:
            blocks[block.qid] = block

        return blocks

    def get_questions(self):
        questions = dict()
        for question in self.questions:
            questions[question.qid] = question

        return questions

    def get_choices(self):
        choices = dict()
        for question in self.questions:
            for choice in question.choices:
                if question.qid not in choices.keys():
                    choices[question.qid] = dict()
                choices[question.qid][choice.qid] = choice

        return choices

    def get_subquestions(self):
        subquestions = dict()
        for question in self.questions:
            for subquestion in question.subquestions:
                if question.qid not in subquestions.keys():
                    subquestions[question.qid] = dict()
                subquestions[question.qid][subquestion.qid] = subquestion

        return subquestions

    def get_embedded_data(self):
        embedded_data = dict()
        for embedded_data in self.embedded_data:
            embedded_data[embedded_data.name] = embedded_data

        return embedded_data


class Block(Base):
    __tablename__ = 'block'

    id = Column(Integer, primary_key=True)
    qid = Column(String(length=50))
    description = Column(sqlalchemy.UnicodeText())
    elements = Column(Integer)

    survey_id = Column(Integer, ForeignKey('survey.id'))
    survey = relationship(Survey, back_populates='blocks')


Survey.blocks = relationship(
    'Block', order_by=Block.id, back_populates='survey', cascade='save-update, merge, delete')


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True)
    qid = Column(String(length=50))
    questionLabel = Column(sqlalchemy.UnicodeText())
    questionText = Column(sqlalchemy.UnicodeText())
    promptText = Column(sqlalchemy.UnicodeText())

    selector = Column(String(length=50))
    subSelector = Column(String(length=50))
    type = Column(String(length=50))

    block_id = Column(Integer, ForeignKey('block.id'))
    survey_id = Column(Integer, ForeignKey('survey.id'))

    block = relationship(Block, back_populates='questions')
    survey = relationship(Survey, back_populates='questions')

Survey.questions = relationship(
    'Question', order_by=Question.id, back_populates='survey', cascade='save-update, merge, delete')
Block.questions = relationship(
    'Question', order_by=Question.id, back_populates='block', cascade='save-update, merge, delete')


class SubQuestion(Base):
    __tablename__ = 'subquestion'

    id = Column(Integer, primary_key=True)
    qid = Column(Integer)

    variableName = Column(String(length=50))
    choiceText = Column(String(length=50))
    description = Column(sqlalchemy.UnicodeText())
    recode = Column(String(length=50))
    textEntry = Column(sqlalchemy.UnicodeText())

    question_id = Column(Integer, ForeignKey('question.id'))
    question = relationship(Question, back_populates='subquestions')

Question.subquestions = relationship(
    'SubQuestion', order_by=SubQuestion.id, back_populates='question', cascade='save-update, merge, delete')


class Choice(Base):
    __tablename__ = 'choice'

    id = Column(Integer, primary_key=True)
    qid = Column(Integer)

    variableName = Column(String(length=50))
    choiceText = Column(sqlalchemy.UnicodeText())
    description = Column(sqlalchemy.UnicodeText())
    recode = Column(String(length=50))
    textEntry = Column(sqlalchemy.UnicodeText())

    question_id = Column(Integer, ForeignKey('question.id'))
    question = relationship(Question, back_populates='choices')

Question.choices = relationship(
    'Choice', order_by=Choice.id, back_populates='question', cascade='save-update, merge, delete')


class EmbeddedData(Base):
    __tablename__ = 'embedded_data'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=50))
    defaultValue = Column(sqlalchemy.UnicodeText())

    survey_id = Column(Integer, ForeignKey('survey.id'))
    survey = relationship(Survey, back_populates='embedded_data')

Survey.embedded_data = relationship(
    'EmbeddedData', order_by=EmbeddedData.id, back_populates='survey', cascade='save-update, merge, delete')


class Respondent(Base):
    __tablename__ = 'respondent'

    id = Column(Integer, primary_key=True)

    ErrorCode = Column(String(length=50))

    ResponseID = Column(String(length=50))
    ResponseSet = Column(String(length=50))
    StartDate = Column(String(length=50))
    EndDate = Column(String(length=50))

    ExternalDataReference = Column(String(length=50))
    Finished = Column(Integer)
    IPAddress = Column(String(length=50))
    LocationAccuracy = Column(Integer)
    LocationLatitude = Column(String(length=50))
    LocationLongitude = Column(String(length=50))

    RecipientEmail = Column(String(length=50))
    RecipientFirstName = Column(String(length=50))
    RecipientLastName = Column(String(length=50))
    Status = Column(Integer)

    survey_id = Column(Integer, ForeignKey('survey.id'))
    survey = relationship(Survey, back_populates='respondents')

Survey.respondents = relationship(
    'Respondent', order_by=Respondent.id, back_populates='survey', cascade='save-update, merge, delete')


class Response(Base):
    __tablename__ = 'response'

    id = Column(Integer, primary_key=True)
    textEntry = Column(sqlalchemy.UnicodeText())

    question_id = Column(Integer)
    subquestion_id = Column(Integer)
    choice_id = Column(Integer)
    embeddeddata_id = Column(Integer)

    respondent_id = Column(Integer, ForeignKey('respondent.id'))
    respondent = relationship(Respondent, back_populates='responses')

Respondent.responses = relationship(
    'Response', order_by=Response.id, back_populates='respondent', cascade='save-update, merge, delete')
