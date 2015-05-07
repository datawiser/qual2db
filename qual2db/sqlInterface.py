##### MySQL Interface #####
###########################

# This file contains the SQL-interface object and all the functions
# that it uses to interface with the MySQL database

# Standard python library
import datetime
import time
import sys

# Local modules
import config

# MySQL python connector. Exits if it is not installed.
try:
    import mysql.connector as sql
except:
    print 'Error: No Python-MySQL ODBC driver found.'
    print 'Install with: R:\CSR\Admin\Computing\Software\MySQL\mysql-connector-python-2.0.3-py2.7.msi'
    print '-'*30
    raw_input('press any key to exit')
    sys.exit()

class sqlInterface(object):
    '''The interface object for communicating with MySQL.'''

    def __init__(self):
        '''Initializes the interface with a new MySQL connection.'''

        try:
            self.cnx.close()
        except:
            self.cnx = None

        try:
            cnx = sql.connect(user = config.sqlUser,
                              password = config.sqlPassword,
                              host = config.sqlHost,
                              database = config.sqlDB)
        except:
            print 'Error: Cannot connect to mysql'
            return False       
        
        self.cnx = cnx

    ####################################################################
    # Functions for querying and managing MySQL data
    ####################################################################

    def list_surveys(self):
        '''Lists all the surveys currently stored in MySQL.'''
        cur = self.cnx.cursor()

        qry = ('SELECT survey_qid,survey_name FROM surveys')
    
        cur.execute(qry)
        result = cur.fetchall()

        return result

    def get_survey_id(self,qid):
        '''Checks if a survey exists in SQL. If so, the MySQL id is returned.'''
        #cnx = mysql_connect()
        cur = self.cnx.cursor()

        cur.execute('SELECT survey_id '
                    'FROM surveys '
                    'WHERE survey_qid = "' + str(qid) + '"')
        try:
            result_id = cur.fetchone()[0]
        except:
            return False
    
        return result_id

    def get_last_mirrored_response(self,sqlid):
        '''Gets the date of the last respondent in sql for the given survey.'''

        cur = self.cnx.cursor()

        qry = ('SELECT MAX(end_date) FROM respondents '
                 'WHERE survey_id='+str(sqlid))
        cur.execute(qry)
        result = cur.fetchone()[0]
        
        return result

    def get_refresh_date(self,sqlid):
        '''Gets the date a survey was last refreshed.'''
        cur = self.cnx.cursor()

        qry = ('SELECT last_refresh FROM surveys '
                 'WHERE survey_id='+str(sqlid))
        cur.execute(qry)
        result = cur.fetchone()[0]
        
        return result

    def countRespondents(self,sqlid):
        '''Returns the number or responsdents in MySQL for the given survey.'''

        cur = self.cnx.cursor()

        qry = ('SELECT COUNT(*) FROM respondents '
                 'WHERE survey_id ='+str(sqlid))
        cur.execute(qry)
        result = cur.fetchone()[0]
        if result == None:
            return 0

        return int(result)

    def stamp_survey(self,sqlid, field='last_refresh'):
        '''Time stamps a survey, given a date field.'''
        
        cur = self.cnx.cursor()

        now = time.time()
        date = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')

        qry = ('UPDATE surveys '
                 'SET ' + field + ' = "' + date + '" '
                 'WHERE survey_id = ' + str(sqlid))

        cur.execute(qry)
        self.cnx.commit()
        
        return True

    def clear_data(self,sqlid,table=None,tablelist=None):
        '''Clears data for a survey from given list of tables.'''
        
        cur = self.cnx.cursor()

        if tablelist is not None:
            for t in tablelist:
                qry = ('DELETE FROM '+t+' '
                         'WHERE survey_id ='+str(sqlid))
                cur.execute(qry)

        elif table is not None:
            qry = ('DELETE FROM '+table+' '
                         'WHERE survey_id ='+str(sqlid))
            cur.execute(qry)
            
        else:
            return False
        
        self.cnx.commit()

        return True

    def delete_survey(self,sqlid):
        '''Deletes a survey from MySQL.'''

        cur = self.cnx.cursor()

        tablelist = ['surveys','questions','choices','answers',
                        'respondents','responses','blocks']
        for t in tablelist:
            qry = ('DELETE FROM '+t+' '
                   'WHERE survey_id ='+str(sqlid))
            cur.execute(qry)

        self.cnx.commit()

        return True

    ############################################################################
    # Functions for uploading and managing data using a MySQL survey object
    ############################################################################

    def upload_survey(self,survey_object):
        '''Adds a survey record given a survey object. Returns the MySQL id.'''

        cur = self.cnx.cursor()
        sqlid = self.get_survey_id(survey_object.qid)

        if sqlid:
            return sqlid
    
        qry = ('INSERT INTO surveys (survey_name,survey_qid,'
                'owner,status,creation_date) '
                'VALUES (%(survey_name)s,%(survey_qid)s,%(owner)s,'
                '%(status)s,%(creation_date)s)'
                )
        data = {'survey_name':survey_object.name,
                'survey_qid':survey_object.qid,
                'owner':survey_object.owner,
                'status':survey_object.status,
                'creation_date':survey_object.creation,
                }

        cur.execute(qry,data)
        self.cnx.commit()

        newid = self.get_survey_id(survey_object.qid)

        return newid

    def upload_blocks(self,survey_object):
        '''Uploads blocks, returns block key.'''

        cur = self.cnx.cursor()

        if self.check_for_blocks(survey_object) is False:

            qry = ('INSERT INTO blocks (survey_id,block_qid,name) '
                   'VALUES (%(survey_id)s,%(block_qid)s,%(name)s)')

            for block in survey_object.schema['blocks']:

                data = {'survey_id':block[0],
                        'block_qid':block[1],
                        'name':block[2]
                        }
                cur.execute(qry,data)

            self.cnx.commit()

        qry = ('SELECT block_id,block_qid FROM blocks '
               'WHERE survey_id ='+ str(survey_object.sqlid))

        cur.execute(qry)
        block_key = cur.fetchall()

        return block_key

    def upload_respondents(self,survey_object):
        '''Uploads the respondents given a survey object. Returns a respondent key.'''

        cur = self.cnx.cursor()
        cur.execute('LOCK TABLES respondents WRITE;')

        qry = ('INSERT INTO respondents (survey_id,respondent_qid,name,email_address,'
                'ip_address,status,start_date,end_date,finished) '
                'VALUES (%(survey_id)s,%(respondent_qid)s,%(name)s,%(email_address)s,%(ip_address)s,'
                '%(status)s,%(start_date)s,%(end_date)s,%(finished)s)'
                )

        for respondent in survey_object.respondents:
            data = {'survey_id':respondent[0],
                    'respondent_qid':respondent[1],
                    'name':respondent[2],
                    'email_address':respondent[3],
                    'ip_address':respondent[4],
                    'status':respondent[5],
                    'start_date':respondent[6],
                    'end_date':respondent[7],
                    'finished':respondent[8]
                    }
            cur.execute(qry,data)

        cur.execute('UNLOCK TABLES;')
        self.cnx.commit()

        qry = ('SELECT respondent_id,respondent_qid '
                'FROM respondents '
                'WHERE survey_id ='+ str(survey_object.sqlid))

        cur.execute(qry)
        key = cur.fetchall()
    
        return key

    def upload_choices(self,survey_object):
        '''Uploads the choices given a survey object. Returns a choice key.'''

        cur = self.cnx.cursor()

        if self.check_for_choices(survey_object) == False:
            cur.execute('LOCK TABLES choices WRITE;')
    
            qry = ('INSERT INTO choices (survey_id,question_id,choice_qid,choice_recode,choice_description,text_entry) '
                    'VALUES (%(survey_id)s,%(question_id)s,%(choice_qid)s,%(choice_recode)s,%(choice_description)s, '
                    '%(text_entry)s)'
                    )
        
            for choice in survey_object.schema['choices']:
                m = [x[0] for x in survey_object.question_key if x[1]==choice[1]]
            
                data = {'survey_id':choice[0],
                        'question_id':m[0],
                        'choice_qid':choice[2],
                        'choice_recode':choice[3],
                        'choice_description':choice[4],
                        'text_entry':choice[5]
                        }
                cur.execute(qry,data)
            self.cnx.commit()
            cur.execute('UNLOCK TABLES;')

        qry = ('SELECT choice_id,choice_qid,question_id '
                'FROM choices '
                'WHERE survey_id ='+ str(survey_object.sqlid))

        cur.execute(qry)
        choice_key = cur.fetchall()

        return choice_key


    def upload_questions(self,survey_object):
        '''Uploads the questions given a survey object. Returns a question key.'''
        
        cur = self.cnx.cursor()

         # Does a simple check for existing questions.
        if self.check_for_questions(survey_object)==False:
            cur.execute('LOCK TABLES questions WRITE;')
            
            qry = ('INSERT INTO questions (survey_id,question_qid,data_type,'
                     'type,selector,sub_selector,export_tag,question_description,question_text,block_id) '
                     'VALUES (%(survey_id)s,%(question_qid)s,%(data_type)s,%(type)s,%(selector)s,%(sub_selector)s, '
                     '%(export_tag)s,%(question_description)s,%(question_text)s,%(block_id)s)'
                     )

            for question in survey_object.schema['schema']:

                headers = ['ResponseID','ExternalDataReference','Name','EmailAddress','IPAddress','Status','StartDate','ResponseSet',
                    'EndDate','Finished','Score','FirstName','LastName']

                edlist = [x[1].replace(' ','') for x in survey_object.schema['ED']]

                exclude = headers + edlist

                try:
                    bid = [x[0] for x in survey_object.block_key if x[1]==question[9]][0]
                except:
                    bid = None

                data = {'survey_id':question[0],
                        'question_qid':question[1],
                        'data_type':question[2],
                        'type':question[3],
                        'selector':question[4],
                        'sub_selector':question[5],
                        'export_tag':question[6],
                        'question_description':question[7],
                        'question_text':question[8],
                        'block_id':bid
                            }

                cur.execute(qry,data)
                
            self.cnx.commit()
            cur.execute('UNLOCK TABLES;')

        qry = ('SELECT question_id,question_qid,type,selector,sub_selector '
                 'FROM questions '
                 'WHERE survey_id ='+str(survey_object.sqlid))

        cur.execute(qry)
        key = cur.fetchall()
        
        return key

    def upload_answers(self,survey_object):
        '''Uploads the answers.'''

        cur = self.cnx.cursor()

        # Does a simple check for existing answers.
        if self.check_for_answers(survey_object) == False:
            cur.execute('LOCK TABLES answers WRITE;')
        
            qry = ('INSERT INTO answers (survey_id,question_id,answer_qid,answer_recode,answer_description) '
                     'VALUES (%(survey_id)s,%(question_id)s,%(answer_qid)s,%(answer_recode)s,%(answer_description)s)'
                     )
            
            for answer in survey_object.schema['answers']:
                m = [x[0] for x in survey_object.question_key if x[1]==answer[1]]
                
                data = {'survey_id':answer[0],
                        'question_id':m[0],
                        'answer_qid':answer[2],
                        'answer_recode':answer[3],
                        'answer_description':answer[4]
                            }

                cur.execute(qry,data)
            self.cnx.commit()
            cur.execute('UNLOCK TABLES;')

        qry = ('SELECT answer_id,answer_qid,question_id '
                 'FROM answers '
                 'WHERE survey_id ='+str(survey_object.sqlid))

        cur.execute(qry)
        answer_key = cur.fetchall()

        return answer_key

    def upload_responses(self,survey_object):
        '''Uploads the responses.'''

        t0 = time.time()
        cur = self.cnx.cursor()

        cur.execute('LOCK TABLES responses WRITE;')

        qry = ('INSERT INTO responses (survey_id,respondent_id,question_id,choice_id,answer_id,answer_text) '
                    'VALUES (%(survey_id)s,%(respondent_id)s,%(question_id)s,%(choice_id)s,%(answer_id)s,%(answer_text)s)'
                     )

        # This is a counter so that for every 1,000 records a message is sent with the total uploaded.
        for num,r in enumerate(survey_object.responses):
            if num == 0:
                pass
            elif (num/1000.0).is_integer():
                print str(num) +' rows'

            data = {'survey_id':r[0],
                    'respondent_id': r[1],
                    'question_id':r[2],
                    'choice_id': r[3],
                    'answer_id':r[4],
                    'answer_text':r[5],
                    }
            
            cur.execute(qry,data)
        
        self.cnx.commit()
        cur.execute('UNLOCK TABLES;')

        print 'UPLOAD TIME:', round(time.time() - t0,2), ' seconds.'
        return True

    ######################################################################
    # Experimental & Checking for data in MySQL
    ######################################################################

    def get_sample_respondent(self,sqlid):
        '''This is for testing.'''

        cur = self.cnx.cursor()

        qry = ('SELECT respondent_qid FROM respondents '
                 'WHERE survey_id ='+str(sqlid)+' '
                 'LIMIT 1')      

        cur.execute(qry)
        result = cur.fetchone()[0]

        return result
    
    def check_for_schema(self,survey_object):
        '''Checks to see if there is data for all schema tables.'''

        checks=[]
        checks.append(check_for_questions(survey_object))
        checks.append(check_for_choices(survey_object))
        checks.append(check_for_answers(survey_object))

        if False in checks:
            return False
        else:
            return True

    def check_for_blocks(self,survey_object):
        '''Checks if all the questions have been loaded to MySQL'''
        
        cur = self.cnx.cursor()

        qry = ('SELECT COUNT(*) FROM blocks '
                 'WHERE survey_id ='+str(survey_object.sqlid))

        cur.execute(qry)
        result = cur.fetchone()[0]

        if int(result) == int(len(survey_object.schema['blocks'])):
            return True
        else:
            return False

    def check_for_questions(self,survey_object):
        '''Checks if all the questions have been loaded to MySQL'''
        
        cur = self.cnx.cursor()

        qry = ('SELECT COUNT(*) FROM questions '
                 'WHERE survey_id ='+str(survey_object.sqlid))

        cur.execute(qry)
        result = cur.fetchone()[0]

        if int(result) == int(len(survey_object.schema['schema'])):
            return True
        else:
            return False

    def check_for_choices(self,survey_object):
        '''Checks if all the choices have been loaded to MySQL'''
        
        cur = self.cnx.cursor()

        qry = ('SELECT COUNT(*) FROM choices '
                 'WHERE survey_id = '+str(survey_object.sqlid))
        
        cur.execute(qry)
        result = cur.fetchone()[0]

        if int(result)>0:
            return True
        else:
            return False

    def check_for_answers(self,survey_object):
        '''Checks if all the answers have been loaded to MySQL'''

        cur = self.cnx.cursor()

        qry = ('SELECT COUNT(*) FROM answers '
                 'WHERE survey_id ='+str(survey_object.sqlid))

        cur.execute(qry)
        result = cur.fetchone()[0]

        if int(result)>0:
            return True
        else:
            return False

    def configure_db(self,overwrite=False):
        '''Sets up all the tables in MySQL.'''

        s = None

        if overwrite is True:
            print '-'*20,'WARNING!','-'*20
            print 'You selected OVERWRITE.'
            print 'This command will DELETE and REPLACE existing tables that are named:'
            print '      surveys, questions, choices, answers, respondents, or responses.'
            print ''
            s = raw_input('Are you sure you want to do this? Type YES to confirm: ')

            print ''

            if s == 'YES':
                print 'Tables will be replaced.'
            else:
                overwrite = False
                print 'Tables will NOT be replaced.'
        
        cur = self.cnx.cursor()

        surveys = '''
        CREATE TABLE `surveys` (
        `survey_id` INT(11) NOT NULL AUTO_INCREMENT,
        `survey_name` VARCHAR(50) NULL DEFAULT NULL,
        `survey_qid` VARCHAR(50) NULL DEFAULT NULL,
        `owner` VARCHAR(50) NULL DEFAULT NULL,
        `status` INT(11) NULL DEFAULT NULL,
        `creation_date` DATETIME NULL DEFAULT NULL,
        `last_refresh` DATETIME NULL DEFAULT NULL,
        `survey_version` DATETIME NULL DEFAULT NULL,
        PRIMARY KEY (`survey_id`)
        )
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
        AUTO_INCREMENT=1
        ;
        '''

        blocks = '''
        CREATE TABLE `blocks` (
        `block_id` INT(11) NOT NULL AUTO_INCREMENT,
        `survey_id` INT(11) NULL DEFAULT NULL,
        `block_qid` VARCHAR(50) NULL DEFAULT NULL,
        `name` VARCHAR(50) NULL DEFAULT NULL,
        PRIMARY KEY (`block_id`)
        )
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
        AUTO_INCREMENT=1
        ;
        '''

        questions = '''
        CREATE TABLE `questions` (
        `question_id` INT(11) NOT NULL AUTO_INCREMENT,
        `survey_id` INT(11) NULL DEFAULT '0',
        `question_qid` VARCHAR(50) NULL DEFAULT '0',
        `data_type` VARCHAR(2) NULL DEFAULT '0',
        `question_description` TEXT NULL,
        `type` VARCHAR(10) NULL DEFAULT '0',
        `selector` VARCHAR(10) NULL DEFAULT '0',
        `export_tag` VARCHAR(50) NULL DEFAULT '0',
        `question_text` TEXT NULL,
        `sub_selector` VARCHAR(50) NULL DEFAULT NULL,
        PRIMARY KEY (`question_id`)
        )
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
        AUTO_INCREMENT=1
        ;
        '''

        choices = '''
        CREATE TABLE `choices` (
        `choice_id` INT(11) NOT NULL AUTO_INCREMENT,
        `survey_id` INT(11) NULL DEFAULT NULL,
        `question_id` INT(11) NULL DEFAULT NULL,
        `choice_qid` INT(11) NULL DEFAULT NULL,
        `choice_recode` VARCHAR(50) NULL DEFAULT NULL,
        `choice_description` MEDIUMTEXT NULL,
        `text_entry` TINYINT(4) NULL DEFAULT NULL,
        `export_tag` VARCHAR(50) NULL DEFAULT NULL,
        PRIMARY KEY (`choice_id`)
        )
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
        AUTO_INCREMENT=1
        ;
        '''

        answers = '''
        CREATE TABLE `answers` (
        `answer_id` INT(11) NOT NULL AUTO_INCREMENT,
        `survey_id` INT(11) NULL DEFAULT '0',
        `question_id` INT(11) NULL DEFAULT '0',
        `answer_qid` INT(11) NULL DEFAULT '0',
        `answer_recode` VARCHAR(50) NULL DEFAULT '0',
        `answer_description` VARCHAR(50) NULL DEFAULT '0',
        PRIMARY KEY (`answer_id`)
        )
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
        AUTO_INCREMENT=1
        ;
        '''

        respondents = '''
        CREATE TABLE `respondents` (
        `respondent_id` INT(11) NOT NULL AUTO_INCREMENT,
        `respondent_qid` VARCHAR(50) NOT NULL DEFAULT '0',
        `survey_id` INT(11) NULL DEFAULT NULL,
        `name` VARCHAR(50) NULL DEFAULT NULL,
        `email_address` VARCHAR(50) NULL DEFAULT NULL,
        `ip_address` VARCHAR(50) NULL DEFAULT NULL,
        `status` INT(11) NULL DEFAULT NULL,
        `start_date` DATETIME NULL DEFAULT NULL,
        `end_date` DATETIME NULL DEFAULT NULL,
        `finished` INT(11) NULL DEFAULT NULL,
        PRIMARY KEY (`respondent_id`)
        )
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
        AUTO_INCREMENT=1
        ;
        '''

        responses = '''
        CREATE TABLE `responses` (
        `response_id` INT(11) NOT NULL AUTO_INCREMENT,
        `survey_id` INT(11) NULL DEFAULT NULL,
        `respondent_id` INT(11) NULL DEFAULT NULL,
        `question_id` INT(11) NULL DEFAULT NULL,
        `matrix_row` INT(11) NULL DEFAULT NULL,
        `choice_id` INT(11) NULL DEFAULT NULL,
        `answer_id` INT(11) NULL DEFAULT NULL,
        `answer_text` TEXT NULL,
        PRIMARY KEY (`response_id`)
        )
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
        AUTO_INCREMENT=1
        ;
        '''

        tables_sql = [surveys,blocks,questions,choices,answers,respondents,responses]
        tables_name = ['surveys','blocks','questions','choices','answers','respondents','responses']

        tables = zip(tables_name,tables_sql)

        for table in tables:
            
            # Check to see if table exists
            cur.execute("SHOW TABLES LIKE '"+table[0]+"'")
            r = cur.fetchone()
            
            if r and (overwrite is True):
                cur.execute('DROP TABLE '+table[0])
                cur.execute(table[1])
                print table[0], 'table replaced.'
                
            elif r:
                continue

            else:
                cur.execute(table[1])
                print table[0], 'added.'
                
        
        self.cnx.commit()

        print 'MySQL configured.'



