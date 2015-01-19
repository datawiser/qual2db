import mysql_api
import qual_request
# import webgui #Experimental
import config
import errors

class Survey(object):
    '''The Qualtrics survey object.'''
    def refresh(self):
        '''Updates the survey's schema information and survey counts.'''
        self.sqlid = mysql_api.get_survey_id(self.qid)

        info = qual_request.getInfo(self.qid)
        if info == False:
            return None

        # Gets the number of respondents in QB and in MySQL for comparison.
        self.qualtrics_responses = info['responses']
        self.mysql_responses = mysql_api.countRespondents(self.qid)

        # This gets the general schema of the survey.
        if self.sqlid == False:
            schema = qual_request.getSchema(self.qid)
        else:
            schema = qual_request.getSchema(self.qid,self.sqlid)

        self.name = schema['name']
        self.owner = schema['owner']
        self.status = schema['status']
        self.creation = schema['creation']
        self.varlist = schema['schema']
        self.schema = schema 

    def describe(self):
        '''Describes survey object.'''
        print 'name:       ' + self.name
        print 'owner:      ' + self.owner
        print 'status:     ' + self.status
        print 'creation:   ' + self.creation
        print 'qualtrics:  ' + str(self.qualtrics_responses)
        print 'mysql:      ' + str(self.mysql_responses)

    def getData(self,startdate=None,enddate=None):
        '''Downloads survey data.'''
        self.data = qual_request.getData(self,startdate=startdate,enddate=enddate)
        
    def align_with_mysql(self):
        '''Adds the survey info and schema to mySQL'''
        cnx = mysql_api.mysql_connect()
        
        self.sqlid = mysql_api.upload_survey(self,cnx)
        schema = qual_request.getSchema(self.qid,self.sqlid)
        self.schema = schema
        
        self.question_key = mysql_api.upload_questions(self,cnx)

        self.choice_key = mysql_api.upload_choices(self,cnx)
        self.answer_key = mysql_api.upload_answers(self,cnx)

        cnx.close()

    def check_upload_time(self):
        '''Calculates the amount of time it should take for the survey to fully upload to MySQL.'''
        if int(self.qualtrics_responses) > 0:

            xml = qual_request.getData(self,limit=1)
            count = qual_request.count_sample_responses(xml)
            rows = count*int(self.qualtrics_responses)
            t = int((rows*0.005)/60.00)
            if t == 0:
                t = '< 1'
            print 'fields:        ' + str(count)
            print 'est-rows:      ' + str(rows)
            print '---------------------------'
            print 'est-time:      ' + str(t) + ' minute(s)'
        else:
            print 'No responses.'
            return False
        
    def update_mysql(self):
        '''Updates MySQL by adding new data from Qualtrics.'''
        # Making sure the survey is aligned with mysql
        self.align_with_mysql()
        
        # Counting respondents currently in MySQL
        self.mysql_responses = mysql_api.countRespondents(self.qid)
        # Timestamping the survey 
        mysql_api.stamp_survey(self)
        
        if self.qualtrics_responses > self.mysql_responses:

            # Getting the last response date and pulling data
            cnx = mysql_api.mysql_connect()
            last_response = mysql_api.get_last_mirrored_response(self,cnx)
            cnx.close()

            print 'Downloading data.'
            self.data = qual_request.getData(self,last_response)

            # Building the respondent list
            self.respondents = qual_request.processRespondents(self,self.sqlid)['respondents']
            cnx = mysql_api.mysql_connect()
            self.respondent_key = mysql_api.upload_respondents(self,cnx)
            cnx.close()

            # Processing the responses to a list and upload
            self.responses = qual_request.processResponses(self,self.sqlid)
            
            cnx = mysql_api.mysql_connect()
            mysql_api.upload_responses(self,cnx)

            # Updating the MySQL response count 
            self.mysql_responses = mysql_api.countRespondents(self.qid)
            cnx.close()
            
            print 'MySQL updated with new Qualtrics responses.'
        else:
            print 'No new data.'

    def mirror_data(self):
        '''Force MySQL survey to mirror Qualtrics data.'''
        cnx = mysql_api.mysql_connect()
        mysql_api.clear_data(self,cnx,tablelist=['Responses','Respondents'])
        self.update_mysql()
        cnx.close()
        
        print 'MySQL data mirrors Qualtrics data.'''

    def overhaul(self):
        '''Rebuilds the MySQL schema tables (use only if the survey schema has changed).'''
        # Deleting all existing MySQL data.
        cnx = mysql_api.mysql_connect()
        mysql_api.clear_data(self,cnx,tablelist=['Questions','Answers','Choices',
                                              'Responses','Respondents'])
        self.align_with_mysql()
        self.mysql_responses = mysql_api.countRespondents(self.qid)
        cnx.close()
        
        print 'MySQL survey has been overhauled and truncated.'

    def clear_data(self):
        '''Clears out all Respondents, and Responses in MySQL.'''
        cnx = mysql_api.mysql_connect()
        mysql_api.clear_data(self,cnx,tablelist=['Responses','Respondents'])
        self.mysql_responses = mysql_api.countRespondents(self.qid)
        cnx.close()

    # Initialization function
    def __init__(self, surveyid):
        '''This is the initialization function.'''
        self.qid = surveyid
        self.refresh()
