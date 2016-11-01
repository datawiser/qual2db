'''

datamodel.py

'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Numeric, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# create the declarative base
Base = declarative_base()

class Survey(Base):
	'''
	resolution in meters.
	'''
	__tablename__ = 'survey'

	id = Column(Integer, primary_key=True)
	qid = Column(String)
	name = Column(String, unique=True)

	isActive = Column(String)
	creationDate = Column(String)
	lastModifiedDate = Column(String)
	ownerId = Column(String)
	organizationId = Column(String)

	auditable = Column(Integer)
	deleted = Column(Integer)
	generated = Column(Integer)

	endDate = Column(String)
	startDate = Column(String)

	def get_blocks(self):
		'''
		'''
		blocks = dict()
		for block in self.blocks:
			blocks[block.qid] = block

		return blocks

	def get_questions(self):
		'''
		'''
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
	'''
	'''
	__tablename__ = 'block'

	id = Column(Integer, primary_key=True)
	qid = Column(String)
	description = Column(String)
	elements = Column(Integer)

	survey_id = Column(Integer, ForeignKey('survey.id'))
	survey = relationship(Survey, back_populates='blocks')


Survey.blocks = relationship('Block', order_by=Block.id, back_populates='survey')


class Question(Base):
	'''
	'''
	__tablename__ = 'question'

	id = Column(Integer, primary_key=True)
	qid = Column(String)
	questionLabel = Column(String)
	questionText = Column(String)
	
	# questionType
	selector = Column(String)
	subSelector = Column(String)
	type = Column(String)

	block_id = Column(Integer, ForeignKey('block.id'))
	survey_id = Column(Integer, ForeignKey('survey.id'))

	block = relationship(Block, back_populates='questions')
	survey = relationship(Survey, back_populates='questions')

Survey.questions = relationship('Question', order_by=Question.id, back_populates='survey')
Block.questions = relationship('Question', order_by=Question.id, back_populates='block')

class SubQuestion(Base):
	'''
	'''
	__tablename__ = 'subquestion'

	id = Column(Integer, primary_key=True)
	qid = Column(Integer)
	
	variableName = Column(String)
	choiceText = Column(String)
	description = Column(String)
	recode = Column(String)
	textEntry = Column(String)

	question_id = Column(Integer, ForeignKey('question.id'))
	question = relationship(Question, back_populates='subquestions')

Question.subquestions = relationship('SubQuestion', order_by=SubQuestion.id, back_populates='question')


class Choice(Base):
	'''
	'''
	__tablename__ = 'choice'

	id = Column(Integer, primary_key=True)
	qid = Column(Integer)
	
	variableName = Column(String)
	choiceText = Column(String)
	description = Column(String)
	recode = Column(String)
	textEntry = Column(String)

	question_id = Column(Integer, ForeignKey('question.id'))
	question = relationship(Question, back_populates='choices')

Question.choices = relationship('Choice', order_by=Choice.id, back_populates='question')


class EmbeddedData(Base):
	'''
	'''
	__tablename__ = 'embedded_data'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	defaultValue = Column(String)
	
	survey_id = Column(Integer, ForeignKey('survey.id'))
	survey = relationship(Survey, back_populates='embedded_data')

Survey.embedded_data = relationship('EmbeddedData', order_by=EmbeddedData.id, back_populates='survey')


class Respondent(Base):
	'''
	'''
	__tablename__ = 'respondent'

	id = Column(Integer, primary_key=True)

	ErrorCode = Column(String)

	ResponseID = Column(String)
	ResponseSet = Column(String)
	StartDate = Column(String)
	EndDate = Column(String)

	ExternalDataReference = Column(String)
	Finished = Column(Integer)
	IPAddress = Column(String)
	LocationAccuracy = Column(Integer)
	LocationLatitude = Column(String)
	LocationLongitude = Column(String)

	RecipientEmail = Column(String)
	RecipientFirstName = Column(String)
	RecipientLastName = Column(String)
	Status = Column(Integer)
	
	survey_id = Column(Integer, ForeignKey('survey.id'))
	survey = relationship(Survey, back_populates='respondents')

Survey.respondents = relationship('Respondent', order_by=Respondent.id, back_populates='survey')


class Response(Base):
	'''
	'''
	__tablename__ = 'response'

	id = Column(Integer, primary_key=True)
	textEntry = Column(String)

	question_id = Column(Integer)
	subquestion_id = Column(Integer)
	choice_id = Column(Integer)
	embeddeddata_id = Column(Integer)
	
	# survey_id = Column(Integer, ForeignKey('survey.id'))
	# survey = relationship(Survey, back_populates='responses')

	respondent_id = Column(Integer, ForeignKey('respondent.id'))
	respondent = relationship(Respondent, back_populates='responses')

	#choice_id = Column(Integer, ForeignKey('choice.id'))
	#choice = relationship(Choice, back_populates='responses')


# Survey.responses = relationship('Response', order_by=Response.id, back_populates='survey')
Respondent.responses = relationship('Response', order_by=Response.id, back_populates='respondent')
#Choice.responses = relationship('Response', order_by=Response.id, back_populates='respondent')

'''
useful objects
'''

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