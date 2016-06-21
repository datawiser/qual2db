##### Qualtrics Interface #####
###############################

# This file contains the Qualtrics-interface object and all the functions
# that it uses to interface with the Qualtrics API

# Standard python library
import xml.etree.ElementTree as ET
import urllib2
import urllib
import time

# Local modules
import config

class qualInterface(object):
    '''The interface object for communication with the Qualtrics API.'''

    def request(self,qid=None,call=None,startdate=None,enddate=None,respondent=None,limit=None,debug=False):
        '''Makes a REST call to Qualatrics. Returns an xml.etree object.'''

        payload = {'Request':call, 'SurveyID': qid,'Format':'XML','Password':config.Password,
               'Token':config.Token,'Version':config.Version,'User':config.User}

        # Set other call parameters
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

        # If debug is set to True, the url is printed
        if debug == True:
            print url

        xml = ET.fromstring(response.read())
        return xml

    #################################################
    # Functions that get information about surveys
    #################################################

    def printSurveys(self):
        '''Lists surveys available to the API account.'''

        l = self.listSurveys()

        for i in l:
            print i[0], i[1][:30]

    def listSurveys(self):
        '''Creates a list of surveys the API account has access to.'''

        xml = self.request(call='getSurveys')

        survey_list = []
        for survey in xml.find('Result/Surveys'):
            qid = survey.find('SurveyID').text
            surveyname = survey.find('SurveyName').text

            survey_list.append([qid,surveyname])

        return survey_list 
            
    def getInfo(self,qid,debug=False):
        '''Creates a dictionary with basic details about a given survey.'''
        
        xml = self.request(qid,'getSurveyName',debug=debug)
     
        responses = xml.find('Result/responses').text
        name = xml.find('Result/SurveyName').text
        status = xml.find('Result/SurveyStatus').text

        if responses is None:
            responses = 0

        survey_info = {'name':name,
                       'responses':int(responses),
                       'status':status}

        return survey_info
    
    def getSchema(self,qid,sqlid=None,debug=False):
        '''Gets a survey's schema.'''
        
        xml = self.request(qid,call='getSurvey',debug=debug)

        # This is for replacing qid with sqlid in the schema
        if sqlid is not None:
            qid = sqlid

        name = xml.find('SurveyName').text
        owner = xml.find('OwnerID').text
        status = xml.find('isActive').text
        creation = xml.find('CreationDate').text
        
        alist = []
        qlist = []
        clist = []
        blist = []

        # This will contain the master key for blocks and questions
        bkey = []

        # Getting all the Block information this will be added to each Question item
        for item in xml.findall('Blocks/Block'):
            bname = item.get('Description')
            bid = item.get('ID')

            for question in item.findall('BlockElements/Question'):
                elementid = question.get('QuestionID')
                bkey.append([bid,elementid])

            blist.append([qid,bid,bname])

        for item in xml.findall('Questions/Question'):

            quid = item.get('QuestionID')
            qtype = item.find('Type').text
            qselector = item.find('Selector').text
            qsubselector = item.find('SubSelector').text
            qtag = item.find('ExportTag').text
            qdesc = item.find('QuestionDescription').text
            qtext = item.find('QuestionText').text

            # Finding the related block
            parseqid = quid.split('_')[-1].split('#')[0]
            bid = [x[0] for x in bkey if x[1]==parseqid][0]

            # Processing the choices for this question
            for choice in item.findall('Choices/Choice'):
                cid = choice.get('ID') # This is the qualtrics assigned id
                crecode = choice.get('Recode')
                cdesc = choice.find('Description').text
                
                textentry = choice.get('TextEntry')
                if textentry == None:
                    textentry = 0
                clist.append([qid,quid,cid,crecode,cdesc,textentry])

            # Processing the answers
            for answer in item.findall('Answers/Answer'):
                aid = answer.get('ID')
                arecode = answer.get('Recode')
                adesc = answer.find('Description').text
                alist.append([qid,quid,aid,arecode,adesc])
           
            # Adding the base question
            append = [qid,quid,'Q',qtype,qselector,qsubselector,qtag,qdesc,qtext,bid]
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
                         'questions':qlist,
                         'blocks':blist
                         }

        return survey_schema

    def getData(self,survey_object,startdate=None,enddate=None,respondent=None,limit=None,debug=False):
        '''Gets survey data. Date format:YYYY-MM-DD hh:mm:ss.'''

        # The Legacy Response Data format is what qual2db relies on for interpreting survey data
        survey_data = self.request(survey_object.qid,'getLegacyResponseData',startdate,enddate,respondent=respondent,limit=limit,debug=debug)        
        
        return survey_data

    ####################################################
    # Functions that process Qualtrics data
        
    def processRespondents(self,survey_object,sqlid=None,crosstab=None):
        '''Create a respondent list with default and custom fields (optional ids) from a raw xml export.'''
        
        respondents = []
        
        if sqlid is not None:
            survey_id = sqlid
        else:
            survey_id = survey_object.qid

        sid = ['SurveyID']
        headers = ['ResponseID','Name','EmailAddress','IPAddress','Status','StartDate',
                    'EndDate','Finished']
        
        if crosstab is not None:
            headers = headers+crosstab
            
        for response in survey_object.data.findall('Response'):
            respondent = [survey_id]
            for item in headers:
                attrb = response.find(item).text  
                respondent.append(attrb)
            respondents.append(respondent)

        headers = sid+headers
        
        result = {'headers':headers,
                  'respondents':respondents
                  }
                
        return result

    def processResponses(self,survey_object,sqlid=None,exclude=None,tags=True,debug=True):
        '''Builds a list of responses using ids (tags optional). Excludes specified fields (exclude).'''
        
        print 'Building responses list.'
        
        t0 = time.time()
        responses = []
        
        surveyid = survey_object.qid

        if sqlid is not None:
            surveyid = sqlid

        # These are all the fields that are being excluded from the response set.
        headers = ['ResponseID','ExternalDataReference','Name','EmailAddress','IPAddress','Status','StartDate','ResponseSet',
                    'EndDate','Finished','Score','FirstName','LastName']
        if exclude:
            headers = headers+exclude

        # Temporary kludge to work around scores in XML for CSR1068 GHH
        if sqlid==106:
            scores = ['MERITOverallScore','ResidentialLife','ConvivialMeals','RealHome','PhysicalandOrganizationalSupport',
                      'ElderWell_beingandAutonomy','MeaningfulLife','OrganizationalDesign','ShahbazimRole','CollaborativeCulture',
                      'EmpoweredStaff','EducationalSystems','LeadershipSupport','ModelSupport']
            headers = headers+scores
 

        # The full list of EDs to skip over (removes spaces)
        edlist = [x[1].replace(' ','') for x in survey_object.schema['ED']]
        
        for num,response in enumerate(survey_object.data.findall('Response')):
            if num == 0:
                pass
            elif (num/100.00).is_integer():
                print str(num)+' rows.'

            # This finds the respondent id and its corresponding MySQL id.
            rid = response.find('ResponseID').text
            response_id = [x[0] for x in survey_object.respondent_key if x[1]==rid][0]

            for question in response:
                # This for loop iterates through every single response for every respondent in the XML data.
                # It figures out how to store each response by its question type.

                qid = question.tag # This is the QID tag associated with each response
                
                parsetag = [None]

                if debug is True:
                    print qid

                # Skipping fields that are already stored under respondents in the respondents table.
                if qid in headers: 
                    continue

                # If the response is embedded data:
                elif qid in edlist:
                    answertext = question.text
                    question_id = [x[0] for x in survey_object.question_key if x[1].replace(' ','')==qid][0]
                    choice_id = None
                    answer_id = None
                
                # If the response is not a respondent field OR embedded data field: 
                else: 
                    parsetag = qid.split('_') # Breaks up the QID tag into parts
                    qid = parsetag[0] # this is the built-in qualtrics id that identifies the question

                    # This checks if the tag is formatted as a "Loop & Merge" question
                    # if so, it modifies the qid and parsetag to account for the differences
                    if '' in parsetag:
                        qid = parsetag[-1]+'_'+parsetag[0]
                        parsetag[0] = qid
                        parsetag = parsetag[:-2]
                
                    # These list comprehenders gather information about the type of question this is,
                    # which is critical for the rest of the process
                    qkey = survey_object.question_key
                    question_type        = [x[2] for x in qkey if x[1]==qid][0]
                    question_selector    = [y[3] for y in qkey if y[1]==qid][0]
                    question_subselector = [z[4] for z in qkey if z[1]==qid][0]

                    # IF THE RESPONSE IS:

                    # Side-by-side
                    if question_type == 'SBS':

                        qid = qid+'#'+str(parsetag[1])
                        choice_qid = parsetag[2]

                        if parsetag[-1]=='TEXT':
                            answer_qid = parsetag[3]
                            answertext = question.text
                        else:
                            answer_qid = question.text
                            answertext = None
                            
                    # Multiple choice: single and Net Promoter Score
                    elif (question_type == 'MC' 
                          and question_selector == 'SAVR' 
                          or question_selector=='DL'
                          or question_selector == 'SB' 
                          or question_selector == 'SACOL' 
                          or question_selector == 'SAHR'
                          or question_selector == 'NPS'):

                        choice_qid = question.text
                        answer_qid = None
                        answertext = None

                        if parsetag[-1] == 'TEXT':
                            # adds the text to the last response's answertext field
                            responses[-1][5] =  question.text
                            continue
                        
                    # Multiple choice: multi
                    elif (question_type == 'MC' 
                          and question_selector == 'MAVR' 
                          or question_selector == 'MAHR' 
                          or question_selector == 'MACOL'):

                        choice_qid = parsetag[1]
                        answer_qid = None
                        answertext = question.text
                        if parsetag[-1] == 'TEXT':
                            # Adds the text to the last response's answertext field
                            responses[-1][5] =  question.text
                            continue
                    
                    # Text: form
                    elif question_selector == 'FORM':
                        choice_qid = parsetag[1]
                        answer_qid = None
                        answertext = question.text
                        
                    # Text: text entry or descriptive text
                    elif (question_type == 'TE'
                          or question_type=='Nominal' 
                          or question_type=='DB'):

                        choice_qid = None
                        answer_qid = None
                        answertext = question.text

                    # Matrix: Bipolar (was misspelled as 'Biploar', is that in Qualtrics?)
                    elif (question_type == 'Matrix'
                          and question_selector == 'Bipolar'):

                        choice_qid = parsetag[1]
                        answer_qid = question.text
                        answertext = None

                    # Matrix: Likert
                    elif (question_type == 'Matrix' 
                          and question_selector == 'Likert'):

                        if question_subselector == 'SingleAnswer' or question_subselector =='DL' :
                            choice_qid = parsetag[1]
                            answer_qid = question.text
                            answertext = None
                        if question_subselector == 'MultipleAnswer':
                            choice_qid = parsetag[1]
                            answer_qid = parsetag[2]
                            answertext = question.text

                    # Matrix: Profile
                    elif (question_type == 'Matrix' 
                          and question_selector == 'Profile'):

                        if question_subselector == 'SingleAnswer' or question_subselector =='DL' :
                            choice_qid = parsetag[1]
                            answer_qid = question.text
                            answertext = None
                        if question_subselector == 'MultipleAnswer':
                            choice_qid = parsetag[1]
                            answer_qid = parsetag[2]
                            answertext = question.text
                            
                    # Matrix: Text Entry
                    elif (question_type == 'Matrix' 
                          and question_selector == 'TE'):
                        choice_qid = parsetag[1]
                        answer_qid = parsetag[2]
                        answertext = question.text

                    # Anything else
                    else:
                        choice_qid = parsetag[1]
                        answer_qid = None
                        answertext = question.text
                          
                    # This section gets the MySQL ids for each part.
                    question_id = [x[0] for x in survey_object.question_key if x[1]==qid][0]

                    if choice_qid is not None:
                        try:
                            choice_id = [x[0] for x in survey_object.choice_key if x[1]==int(choice_qid) and x[2]==question_id][0]
                        except:
                           choice_id=None 
                    else:
                        choice_id=None

                    if answer_qid is not None:
                        try:
                            answer_id = [x[0] for x in survey_object.answer_key if x[1]==int(answer_qid) and x[2]==question_id][0]
                        except:
                            answer_id=None
                    else:
                        answer_id = None
                    
                # Adding the response to the list of responses
                responses.append([surveyid,response_id,question_id,choice_id,answer_id,answertext])

        print 'PROCESS TIME:',round(time.time() - t0,2), 'seconds.'
        return responses





