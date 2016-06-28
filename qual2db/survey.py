##### Survey Object & Management #######
########################################

# Local modules
from sqlInterface import sqlInterface
from qualInterface import qualInterface

#############################################
# Survey Object
#############################################

class survey(object):
    '''The Qualtrics survey object.'''
    def refresh(self,debug=False):
        '''Updates the survey's schema information and survey counts.'''
        
        self.sqlid = self.sqlInterface.get_survey_id(self.qid)

        info = self.qualInterface.getInfo(self.qid,debug=debug)

        # Gets the number of respondents in QB and in MySQL for comparison.
        self.qualtrics_responses = info['responses']
        self.mysql_responses = self.sqlInterface.countRespondents(self.sqlid)

        # This gets the general schema of the survey.
        if self.sqlid == False:
            schema = self.qualInterface.getSchema(self.qid,debug=debug)
            refresh_date = False
        else:
            schema = self.qualInterface.getSchema(self.qid,self.sqlid,debug=debug)
            refresh_date = self.sqlInterface.get_refresh_date(self.sqlid)
            

        self.name = schema['name']
        self.owner = schema['owner']
        self.status = schema['status']
        self.creation = schema['creation']
        self.varlist = schema['schema']
        self.schema = schema
        self.refresh_date = refresh_date 

    def describe(self):
        '''Describes survey object.'''
        print 'name:           ' + self.name
        print 'qid:            ' + self.qid
        print 'owner:          ' + self.owner
        print 'status:         ' + self.status
        print 'creation:       ' + self.creation
        print 'sqlid:          ' + str(self.sqlid)
        print 'last refresh:   ' + str(self.refresh_date)
        print 'qualtrics:      ' + str(self.qualtrics_responses)
        print 'mysql:          ' + str(self.mysql_responses)

    def get_data(self,startdate=None,enddate=None,debug=False):
        '''Downloads survey data.'''
        self.data = self.qualInterface.getData(self,startdate=startdate,enddate=enddate,debug=debug)
   
    def align_with_sql(self,debug=False):
        '''Adds the survey info and schema to mySQL'''

        self.sqlid = self.sqlInterface.upload_survey(self)
        self.schema = self.qualInterface.getSchema(self.qid,self.sqlid,debug=debug)

        self.block_key = self.sqlInterface.upload_blocks(self)
        
        self.question_key = self.sqlInterface.upload_questions(self)

        self.choice_key = self.sqlInterface.upload_choices(self)
        self.answer_key = self.sqlInterface.upload_answers(self)

        self.refresh()
        print 'aligned with sql.'
        
    def update_sql(self,debug=False):
        '''Updates MySQL by adding new data from Qualtrics.'''
        # Making sure the survey is aligned with mysql
        self.align_with_sql()

        last_response = self.sqlInterface.get_last_mirrored_response(self.sqlid)
        #refresh_date = self.sqlInterface.get_refresh_date(self.sqlid)

        print 'Gathering qualtrics data.'
        self.data = self.qualInterface.getData(self,startdate=last_response,debug=debug)
        self.respondents = self.qualInterface.processRespondents(self,self.sqlid)['respondents']

        # this is a list of respondents in MySQL
        respondent_list = [x for ]

        if len(self.respondents) > 0:

            print len(self.respondents), 'new responses.'

            # Refresh the connection I & process/upload respondents
            self.sqlInterface.__init__()
            self.respondent_key = self.sqlInterface.upload_respondents(self)

            # Refresh the connection II & process/uploads responses
            self.responses = self.qualInterface.processResponses(self,self.sqlid,debug=debug)

            self.sqlInterface.__init__()
            self.sqlInterface.upload_responses(self)

            # Refreshing info
            self.refresh(debug=debug)

            print 'MySQL updated with new Qualtrics responses.'
        else:
            print 'No new data.'

        self.sqlInterface.stamp_survey(self.sqlid)
        self.refresh()

    def overhaul(self):
        '''Rebuilds the MySQL schema tables (use only if the survey schema has changed).'''
        
        # Deleting all existing MySQL data.
        self.sqlInterface.clear_data(self.sqlid,tablelist=['questions','answers','choices','responses','respondents',
                                                            'blocks'])
        self.align_with_sql()
        self.refresh()
        
        print 'MySQL survey has been overhauled and truncated.'

    def clear_data(self):
        '''Clears out all Respondents, and Responses in MySQL.'''

        self.sqlInterface.clear_data(self.sqlid,tablelist=['responses','respondents'])
        self.refresh()

    def remove(self):
        '''Removes the survey, its schema and data, from MySQL.'''

        self.sqlInterface.delete_survey(self.sqlid)
        self.refresh()

    # Initialization function
    def __init__(self, qid):
        '''This is the initialization function.'''
        self.qid = qid

        self.sqlInterface = sqlInterface()
        self.qualInterface = qualInterface()
        
        self.refresh()
