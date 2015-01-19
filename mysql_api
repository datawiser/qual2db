# This file contains all the functions that involve
# a connection to the MySQL database. 

import datetime
import time

import mysql.connector as sql

import config
import errors

def mysql_connect(warnings=True):
    '''Opens a connection to MySQL.'''
    try:
        cnx = sql.connect(user = config.sqlUser,
                          password = config.sqlPassword,
                          host = config.sqlHost,
                          database = config.sqlDB)
    except:
        raise errors.ConnectionError()       
    return cnx

def check_table(table):
    '''Checks to see if a table exists.'''
    cnx = mysql_connect()
    cur = cnx.cursor()
    
    cur.execute('SELECT COUNT(*) '
                'FROM information_schema.tables '
                'WHERE table_name = "' + table + '"')

    if cur.fetchone()[0] == 1:
        cnx.close()
        return True
    cnx.close()
    return False

# This function is still being built    
def check_configuraton():
    '''Checks to see if mySQL is configured correctly.'''
    cnx = mysql_connect()
    cur = cnx.cursor()

    required_tables = ['Responses','Respondents','Questions','Surveys']
                    #'answers','blocks']

    for table in required_tables:
        test = check_table(table)
        if test==False:
            cnx.close()
            return False
        else:
            pass
    cnx.close()
    return True

def get_survey_id(surveyid):
    '''Checks if a survey exists in SQL. If so, the MySQL id is returned'''
    cnx = mysql_connect()
    cur = cnx.cursor()

    cur.execute('SELECT SurveyID '
                'FROM Surveys '
                'WHERE SurveyQID = "' + str(surveyid) + '"')
    try:
        result_id = cur.fetchone()[0]
    except:
        cnx.close()
        return False
    cnx.close()
    return result_id

##############################################################
# These functions upload data into MySQL

def upload_survey(survey,cnx):
    '''Adds a survey record. Requires a SQL connections (cnx)'''
    cur = cnx.cursor()
    sqlid = get_survey_id(survey.qid)

    if sqlid:
        return sqlid
    
    query = ('INSERT INTO Surveys (SurveyName,SurveyQID,'
             'Owner,Status,CreationDate) '
             'VALUES (%(SurveyName)s,%(SurveyQID)s,%(Owner)s,'
             '%(Status)s,%(CreationDate)s)'
             )
    data = {'SurveyName':survey.name,
            'SurveyQID':survey.qid,
            'Owner':survey.owner,
            'Status':survey.status,
            'CreationDate':survey.creation,
            }
    cur.execute(query,data)
    cnx.commit()

    newid = get_survey_id(survey.qid)

    return newid

def upload_respondents(survey,cnx):
    '''Upload respondents from a list. Returns a respondent key.'''
    cur = cnx.cursor()

    cur.execute('LOCK TABLES Respondents WRITE;')
    
    query = ('INSERT INTO Respondents (SurveyID,RespondentQID,Name,EmailAddress,'
             'IPAddress,Status,StartDate,EndDate,Finished) '
             'VALUES (%(SurveyID)s,%(RespondentQID)s,%(Name)s,%(EmailAddress)s,%(IPAddress)s,'
             '%(Status)s,%(StartDate)s,%(EndDate)s,%(Finished)s)'
             )
    for respondent in survey.respondents:
        data = {'SurveyID':respondent[0],
                'RespondentQID':respondent[1],
                'Name':respondent[2],
                'EmailAddress':respondent[3],
                'IPAddress':respondent[4],
                'Status':respondent[5],
                'StartDate':respondent[6],
                'EndDate':respondent[7],
                'Finished':respondent[8]
                    }
        cur.execute(query,data)
    cur.execute('UNLOCK TABLES;')
    cnx.commit()

    query = ('SELECT RespondentID,RespondentQID '
             'FROM Respondents '
             'WHERE SurveyID ='+ str(survey.sqlid))

    cur.execute(query)
    key = cur.fetchall()
    
    return key

def upload_choices(survey,cnx):
    '''Uploads the choices'''
    cur = cnx.cursor()

    # Does a rudimentary check for existing choices.
    if check_for_choices(survey,cnx)==False:
        cur.execute('LOCK TABLES Choices WRITE;')
    
        query = ('INSERT INTO Choices (SurveyID,QuestionID,ChoiceQID,ChoiceRecode,ChoiceDescription,TextEntry) '
                 'VALUES (%(SurveyID)s,%(QuestionID)s,%(ChoiceQID)s,%(ChoiceRecode)s,%(ChoiceDescription)s, '
                 '%(TextEntry)s)'
                 )
        
        for choice in survey.schema['choices']:
            m = [x[0] for x in survey.question_key if x[1]==choice[1]]
            
            data = {'SurveyID':choice[0],
                    'QuestionID':m[0],
                    'ChoiceQID':choice[2],
                    'ChoiceRecode':choice[3],
                    'ChoiceDescription':choice[4],
                    'TextEntry':choice[5]
                        }
            cur.execute(query,data)
        cnx.commit()
        cur.execute('UNLOCK TABLES;')

    query = ('SELECT ChoiceID,ChoiceQID,QuestionID '
             'FROM Choices '
             'WHERE SurveyID ='+ str(survey.sqlid))

    cur.execute(query)
    choice_key = cur.fetchall()

    return choice_key

def upload_questions(survey,cnx):
    '''Uploads the questions'''
    cur = cnx.cursor()

     # Does a rudimentary check for existing questions.
    if check_for_questions(survey,cnx)==False:
        cur.execute('LOCK TABLES Questions WRITE;')
        
        query = ('INSERT INTO Questions (SurveyID,QuestionQID,DataType,'
                 'Type,Selector,SubSelector,ExportTag,QuestionDescription,QuestionText) '
                 'VALUES (%(SurveyID)s,%(QuestionQID)s,%(DataType)s,%(Type)s,%(Selector)s,%(SubSelector)s, '
                 '%(ExportTag)s,%(QuestionDescription)s,%(QuestionText)s)'
                 )

        for question in survey.schema['schema']:
            data = {'SurveyID':question[0],
                    'QuestionQID':question[1],
                    'DataType':question[2],
                    'Type':question[3],
                    'Selector':question[4],
                    'SubSelector':question[5],
                    'ExportTag':question[6],
                    'QuestionDescription':question[7],
                    'QuestionText':question[8]
                        }
            cur.execute(query,data)
            
        cnx.commit()
        cur.execute('UNLOCK TABLES;')

    query = ('SELECT QuestionID,QuestionQID,Type,Selector,SubSelector '
             'FROM Questions '
             'WHERE SurveyID ='+str(survey.sqlid))

    cur.execute(query)
    key = cur.fetchall()
    return key

def upload_answers(survey,cnx):
    '''Uploads the answers.'''
    if cnx == False:
        return False
    cnx = mysql_connect()
    cur = cnx.cursor()

     # Does a rudimentary check for existing answers.
    if check_for_answers(survey,cnx)==False:
        cur.execute('LOCK TABLES Answers WRITE;')
    
        query = ('INSERT INTO Answers (SurveyID,QuestionID,AnswerQID,AnswerRecode,AnswerDescription) '
                 'VALUES (%(SurveyID)s,%(QuestionID)s,%(AnswerQID)s,%(AnswerRecode)s,%(AnswerDescription)s)'
                 )
        
        for answer in survey.schema['answers']:
            m = [x[0] for x in survey.question_key if x[1]==answer[1]]
            
            data = {'SurveyID':answer[0],
                    'QuestionID':m[0],
                    'AnswerQID':answer[2],
                    'AnswerRecode':answer[3],
                    'AnswerDescription':answer[4]
                        }
            cur.execute(query,data)
        cnx.commit()
        cur.execute('UNLOCK TABLES;')

    query = ('SELECT AnswerID,AnswerQID,QuestionID '
             'FROM Answers '
             'WHERE SurveyID ='+str(survey.sqlid))

    cur.execute(query)
    answer_key = cur.fetchall()

    return answer_key

def upload_responses(survey,cnx):
    '''Uploads the responses.'''
    print 'Uploading Responses to MySQL.'
    t0 = time.time()
    cur = cnx.cursor()

    cur.execute('LOCK TABLES Responses WRITE;')

    query = ('INSERT INTO Responses (SurveyID,RespondentID,QuestionID,ChoiceID,AnswerID,AnswerText) '
                'VALUES (%(SurveyID)s,%(RespondentID)s,%(QuestionID)s,%(ChoiceID)s,%(AnswerID)s,%(AnswerText)s)'
                 )

    # This is a counter so that for every 1,000 records a message is sent with the total uploaded.
    for num,r in enumerate(survey.responses):
        if num == 0:
            pass
        elif (num/1000.0).is_integer():
            print str(num)+' rows'

        data = {'SurveyID':r[0],
                'RespondentID': r[1],
                'QuestionID':r[2],
                'ChoiceID': r[3],
                'AnswerID':r[4],
                'AnswerText':r[5],
                }
        
        cur.execute(query,data)
    
    cnx.commit()
    cur.execute('UNLOCK TABLES;')
    print 'UPLOAD TIME:',time.time() - t0, 'seconds.'
    return True

############################################################
# These funtions are for filtering and summarizing sql data

def listSurveys():
    cnx = mysql_connect()
    cur = cnx.cursor()

    query = ('SELECT SurveyQID,SurveyName FROM Surveys')
    
    cur.execute(query)
    result = cur.fetchall()
    
    cnx.close()
    return result

def get_last_mirrored_response(survey,cnx):
    cur = cnx.cursor()

    query = ('SELECT MAX(EndDate) FROM Respondents '
             'WHERE SurveyID='+str(survey.sqlid))
    cur.execute(query)
    result = cur.fetchone()[0]
    return result

def countRespondents(surveyid):
    '''Returns the number or responsdents in MySQL for the given survey.'''
    cnx = mysql_connect(warnings=False)
    cur = cnx.cursor()

    sqlid = get_survey_id(surveyid)

    query = ('SELECT COUNT(*) FROM Respondents '
             'WHERE SurveyID ='+str(sqlid))
    cur.execute(query)
    result = cur.fetchone()[0]
    if result == None:
        return 0
    cnx.close()
    return int(result)

#####################################################
# Managing data in MySQL that already exists

def stamp_survey(survey, field='LastRefresh'):
    '''Time stamp a survey, given a date field.'''
    cnx = mysql_connect()
    cur = cnx.cursor()

    now = time.time()
    date = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')

    query = ('UPDATE Surveys '
             'SET ' + field + ' = "' + date + '" '
             'WHERE SurveyID = ' + str(survey.sqlid))

    cur.execute(query)
    cnx.commit()
    cnx.close()
    
    return True

def clear_data(survey,cnx,table=None,tablelist=None):
    '''Clears data for survey from given list of tables.'''
    cur = cnx.cursor()

    if table == None:
        for t in tablelist:
            query = ('DELETE FROM '+t+' '
                     'WHERE SurveyID ='+str(survey.sqlid))
            cur.execute(query)
    elif tablelist == None:
        query = ('DELETE FROM '+table+' '
                     'WHERE SurveyID ='+str(survey.sqlid))
        cur.execute(query)
    else:
        return 'No tables selected.'
    cnx.commit()
    cnx.close()
    return True

# Still working on this
def build_crosstab(survey,cnx,fields=[None]):
    '''Creates a crosstab view for the given survey with the given fields.'''

    query = ('CREATE VIEW ' + survey.name + '_crosstab AS '
             'SELECT Respondents.SurveyID AS SurveyID, '
             'Responses.RespondentID AS RespondentID ')

    return None

#####################################################
# The following functions are for checking to see if
# the survey's querstions, choices, and answers, have
# been uploaded to MySQL

def get_sample_respondent(survey,cnx):
    '''For testing.'''
    if cnx == False:
        return False
    cur = cnx.cursor()

    query = ('SELECT RespondentQID FROM Respondents '
             'WHERE SurveyID ='+str(survey.sqlid)+' '
             'LIMIT 1')      

    cur.execute(query)
    result = cur.fetchone()[0]

    return result
    
def check_for_schema(survey,cnx):
    checks=[]
    checks.append(check_for_questions(survey,cnx))
    checks.append(check_for_choices(survey,cnx))
    checks.append(check_for_answers(survey,cnx))

    if False in checks:
        return False
    else:
        return True

def check_for_questions(survey,cnx):
    '''Checks if all the questions have been loaded to MySQL'''
    cur = cnx.cursor()

    query = ('SELECT COUNT(*) FROM Questions '
             'WHERE SurveyID ='+str(survey.sqlid))
    cur.execute(query)
    result = cur.fetchone()[0]
    if int(result) == int(len(survey.schema['schema'])):
        return True
    else:
        return False

def check_for_choices(survey,cnx):
    '''Checks if all the choices have been loaded to MySQL'''
    cur = cnx.cursor()

    query = ('SELECT COUNT(*) FROM Choices '
             'WHERE SurveyID ='+str(survey.sqlid))
    cur.execute(query)
    result = cur.fetchone()[0]
    if int(result)>0:
        return True
    else:
        return False

def check_for_answers(survey,cnx):
    '''Checks if all the answers have been loaded to MySQL'''
    cur = cnx.cursor()

    query = ('SELECT COUNT(*) FROM Answers '
             'WHERE SurveyID ='+str(survey.sqlid))
    cur.execute(query)
    result = cur.fetchone()[0]
    if int(result)>0:
        return True
    else:
        return False

