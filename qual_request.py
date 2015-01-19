# These functions are for connecting to Qualtrics and
# reshaping Qualtrics data.

import xml.etree.ElementTree as ET
import urllib2
import urllib
import time

import config 
import errors

def qual_request(surveyid=None,call=None,startdate=None,enddate=None,respondent=None,limit=None,debug=False):
    '''Makes a REST call to Qualatrics. Returns an xml.etree object.'''

    payload = {'Request':call, 'SurveyID': surveyid,'Format':'XML','Password':config.Password,
           'Token':config.Token,'Version':config.Version,'User':config.User}

    if call == 'getLegacyResponseData':
        payload['ExportQuestionIDs']='1'
        #payload['UnansweredRecode']='-99'
    if respondent is not None:
        payload['RespondentID']= respondent
    if limit is not None:
        payload['Limit']= limit
    if startdate is not None:
        payload['StartDate']= startdate
    if enddate is not None:
        payload['EndDate']= enddate

    try:
        request = urllib2.Request(config.baseurl, urllib.urlencode(payload))
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, error:
        response = error.read()

    url = response.geturl()+request.data
    if debug == True:
        print url
    xml = ET.fromstring(response.read())
    return xml

#################################################
# Functions that get information about surveys

def listSurveys():
    '''Creates a list of surveys the API account has access to.'''

    xml = qual_request(call='getSurveys')

    surveylist = []
    for survey in xml.find('Result/Surveys'):
        surveyid = survey.find('SurveyID').text
        surveyname = survey.find('SurveyName').text

        surveylist.append([surveyid,surveyname])

    return surveylist 
            
def getInfo(surveyid,debug=False):
    '''Gets basic info about a survey.'''
    
    xml = qual_request(surveyid,'getSurveyName',debug=debug)

    if xml == False:
        return False
 
    responses = xml.find('Result/responses').text
    name = xml.find('Result/SurveyName').text
    status = xml.find('Result/SurveyStatus').text

    if responses is None:
        responses = 0
        
    survey_info = {'name':name,
                   'responses':int(responses),
                   'status':status}
            
    return survey_info
    
def getSchema(surveyid,sqlid=None):
    '''Gets a survey's schema.'''
    
    xml = qual_request(surveyid,'getSurvey')
    if xml == False:
        return False

    if sqlid is not None:
        surveyid = sqlid

    name = xml.find('SurveyName').text
    owner = xml.find('OwnerID').text
    status = xml.find('isActive').text
    creation = xml.find('CreationDate').text
    
    alist = []
    qlist = []
    clist = []
    for item in xml.findall('Questions/Question'):

        qid = item.get('QuestionID')
        qtype = item.find('Type').text
        qselector = item.find('Selector').text
        qsubselector = item.find('SubSelector').text
        qtag = item.find('ExportTag').text
        qdesc = item.find('QuestionDescription').text
        qtext = item.find('QuestionText').text

        num_text_boxes = 0 # This is the number of text entry boxes for the question

        # Processing the choices
        for choice in item.findall('Choices/Choice'):
            cid = choice.get('ID') # This is the qualtrics assigned id
            crecode = choice.get('Recode')
            cdesc = choice.find('Description').text
            
            textentry = choice.get('TextEntry')
            if textentry == None:
                textentry = 0
            clist.append([surveyid,qid,cid,crecode,cdesc,textentry])

        # Processing the answers
        for answer in item.findall('Answers/Answer'):
            aid = answer.get('ID')
            arecode = answer.get('Recode')
            adesc = answer.find('Description').text
            alist.append([surveyid,qid,aid,arecode,adesc])
       
        # Adding the base question
        append = [surveyid,qid,'Q',qtype,qselector,qsubselector,qtag,qdesc,qtext]
        qlist.append(append)

    # Getting the embedded data    
    edlist = []    
    for item in xml.findall('EmbeddedData/Field'):
        
        edtype = item.get('Type')
        edfield = item.find('Name').text
        append = [edfield,'ED',edtype,'','',edfield,'','']
        if sqlid is not None:
            append = [sqlid]+append
        edlist.append(append)

    schema = edlist+qlist
        
    survey_schema = {'name':name,
                     'owner':owner,
                     'status':status,
                     'creation':creation,
                     'answers':alist,
                     'choices':clist,
                     'ED': edlist,
                     'schema':schema,
                     'questions':qlist
                     }

    return survey_schema

def getData(survey,startdate=None,enddate=None,respondent=None,limit=None,debug=False):
    '''Gets survey data. Date format:YYYY-MM-DD hh:mm:ss.'''
    survey_data = qual_request(survey.qid,'getLegacyResponseData',startdate,enddate,respondent=respondent,limit=limit,debug=debug)        
    return survey_data

####################################################
# Functions that process Qualtrics data

def count_sample_responses(xml):
    '''Counts the number of responses that one respondents has.'''
    count = 0
    for num,question in enumerate(xml.find('Response')):
        count += 1

    return count
        
def processRespondents(survey,sqlid=None,crosstab=None):
    '''Create a respondent list with default and custom fields (optional ids) from a raw xml export.'''
    surveyid = survey.qid
    respondents = []
    
    if sqlid is not None:
        surveyid = sqlid

    sid = ['SurveyID']
    headers = ['ResponseID','Name','EmailAddress','IPAddress','Status','StartDate',
                'EndDate','Finished']
    
    if crosstab is not None:
        headers = headers+crosstab
        
    for response in survey.data.findall('Response'):
        respondent = [surveyid]
        for item in headers:
            attrb = response.find(item).text  
            respondent.append(attrb)
        respondents.append(respondent)

    headers = sid+headers
    
    result = {'headers':headers,
              'respondents':respondents
              }
            
    return result

def processResponses(survey,sqlid=None,exclude=None,tags=True):
    '''Builds a list of responses using ids (tags optional). Excludes specified fields (exclude).'''
    print 'Building responses list.'
    t0 = time.time()
    responses = []
    surveyid = survey.qid

    if sqlid is not None:
        surveyid = sqlid

    # These are all the fields that are being excluded from the response set.
    headers = ['ResponseID','ExternalDataReference','Name','EmailAddress','IPAddress','Status','StartDate','ResponseSet',
                'EndDate','Finished','Score']
    if exclude:
        headers = headers+exclude

    #survey.respondent_key
    #survey.question_key

    # list of EDs to skip over
    edlist = [x[1] for x in survey.schema['ED']]
    
    for num,response in enumerate(survey.data.findall('Response')):
        if num == 0:
            pass
        elif (num/100.00).is_integer():
            print str(num)+' rows.'

        rid = response.find('ResponseID').text
        response_id = [x[0] for x in survey.respondent_key if x[1]==rid][0]

        for question in response:
            qid = question.tag
            parsetag =[None]

            if qid in headers: # Skipping respondent fields
                continue
            elif qid in edlist:
                answertext = question.text
                question_id = [x[0] for x in survey.question_key if x[1]==qid][0]
                choice_id = None
                answer_id = None
                
            else: # Everything else
                parsetag = qid.split('_')
                qid = parsetag[0] # this is the built-in qualtrics id               
            
                question_type = [x[2] for x in survey.question_key if x[1]==qid][0]
                question_selector = [x[3] for x in survey.question_key if x[1]==qid][0]
                question_subselector = [x[4] for x in survey.question_key if x[1]==qid][0]

                # Side-By-Side
                if question_type == 'SBS':
                    qid = qid+'#'+str(parsetag[1])
                    choice_qid = parsetag[2]

                    if parsetag[-1]=='TEXT':
                        answer_qid = parsetag[3]
                        answertext = question.text
                    else:
                        answer_qid = question.text
                        answertext = None
                        
                # Multiple choice: single
                elif (question_type == 'MC' and question_selector == 'SAVR' or question_selector=='DL'
                      or question_selector == 'SB' or question_selector == 'SACOL' or question_selector == 'SAHR'
                      or question_selector == 'NPS'):
                    choice_qid = question.text
                    answer_qid = None
                    answertext = None
                    if parsetag[-1] == 'TEXT':
                        # adds the text to the last response's answertext field
                        responses[-1][5] =  question.text
                        continue
                    
                # Multiple choice: multi
                elif (question_type == 'MC' and question_selector == 'MAVR' or question_selector == 'MAHR' or
                      question_selector == 'MACOL'):
                    choice_qid = parsetag[1]
                    answer_qid = None
                    answertext = question.text
                    if parsetag[-1] == 'TEXT':
                        # Adds the text to the last response's answertext field
                        responses[-1][5] =  question.text
                        continue
                
                # Text: Form
                elif question_selector == 'FORM':
                    choice_qid = parsetag[1]
                    answer_qid = None
                    answertext = question.text
                    
                # Text: text entry, embedded data, and descriptive text
                elif question_type == 'TE' or question_type=='Nominal' or question_type=='DB':
                    choice_qid = None
                    answer_qid = None
                    answertext = question.text

                # Matrix: Bipolar
                elif question_type == 'Matrix' and question_selector == 'Biploar':
                    choice_qid = parsetag[1]
                    answer_qid = question.text
                    answertext = None

                # Matrix: Likert
                elif question_type == 'Matrix' and question_selector == 'Likert':
                    if question_subselector == 'SingleAnswer' or question_subselector =='DL' :
                        choice_qid = parsetag[1]
                        answer_qid = question.text
                        answertext = None
                    if question_subselector == 'MultipleAnswer':
                        choice_qid = parsetag[1]
                        answer_qid = parsetag[2]
                        answertext = question.text

                # Matrix: Profile
                elif question_type == 'Matrix' and question_selector == 'Profile':
                    if question_subselector == 'SingleAnswer' or question_subselector =='DL' :
                        choice_qid = parsetag[1]
                        answer_qid = question.text
                        answertext = None
                    if question_subselector == 'MultipleAnswer':
                        choice_qid = parsetag[1]
                        answer_qid = parsetag[2]
                        answertext = question.text

                # Everything else
                else:
                    choice_qid = parsetag[1]
                    answer_qid = None
                    answertext = question.text
                    
                    
                # Getting the MySQL ids
                question_id = [x[0] for x in survey.question_key if x[1]==qid][0]

                if choice_qid is not None:
                    try:
                        choice_id = [x[0] for x in survey.choice_key if x[1]==int(choice_qid) and x[2]==question_id][0]
                    except:
                       choice_id=None 
                else:
                    choice_id=None

                if answer_qid is not None:
                    try:
                        answer_id = [x[0] for x in survey.answer_key if x[1]==int(answer_qid) and x[2]==question_id][0]
                    except:
                        answer_id=None
                else:
                    answer_id = None
                
            # Adding the response to the list of responses
            responses.append([surveyid,response_id,question_id,choice_id,answer_id,answertext])

    print 'PROCESS TIME:',time.time() - t0, 'seconds.'
    return responses
