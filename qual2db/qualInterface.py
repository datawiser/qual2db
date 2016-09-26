##### Qualtrics Interface #####
###############################

# This file contains the Qualtrics-interface object and all the functions
# that it uses to interface with the Qualtrics API

# Standard python library
import xml.etree.ElementTree as ET
import json
import urllib2
import urllib
import time
import zipfile
import os

import requests

# Local modules
import config

class qualInterface(object):
    '''The interface object for communication with the Qualtrics API.'''

    def api_request(self,call='surveys',method='GET',parms=None,export=False,debug=False):
        
        url = config.baseurl+call
        
        headers = {
        'x-api-token': config.Token,
        'content-type' : 'application/json'
        }

        if parms:
            parms = json.dumps(parms)

        response = requests.request(method,url,data=parms,headers=headers)

        # if the request is marked as a data download, write it to a zip file and extract it
        if export:

            qid = call.replace('responseexports/','').replace('/file','')
            path = config.download_directory+qid

            with open(path+'.zip', 'w') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            zipfile.ZipFile(path+'.zip').extractall(path)

            return path

        try:
            data = response.json()
        except:
            return response.text

        return data['result']
    
    def listSurveys(self,debug=False):
        '''Creates a list of surveys the API account has access to.'''

        data = self.api_request(call='surveys',debug=debug)

        survey_list = []
        for survey in data['elements']:
            qid = survey['id']
            name = survey['name']
            active = survey['isActive']

            survey_list.append([qid,name,active])

        return survey_list

    def printSurveys(self):
        '''Quickly lists surveys available to the API account.'''

        surveys = self.listSurveys()

        for survey in surveys:
            print survey[0], survey[1], survey[2]

    # This function should be in the survey object, but I am leaving it here
    # so that the qualInterface can be use to see info about surveys.
    def getInfo(self,qid,debug=False):
        '''Quickly creates a dictionary with basic details about a given survey.'''
        
        schema = self.api_request(call='surveys/'+qid,debug=debug)

        name = schema['name']
        responses = schema['responseCounts']
        active = schema['isActive']

        info = {'name':name,'responses':responses,'active':active}

        return info

########################################################################################################################
# FUNCTIONS FOR GETTING DATA
########################################################################################################################

    def getSchema(self,qid,debug=False):
        '''Downloads the schema dictionary for a given survey'''
        
        schema = self.api_request(call='surveys/'+qid,debug=debug)

        return schema

    def getData(self,qid,last_response=None,debug=False):
        '''Gets survey data.'''

        parms = {
        "surveyId" : qid,
        "format": "json"
        }

        if last_response:
            parms['lastResponseId'] = last_response

        print 'Downloading data.'
        data = self.api_request(call='responseexports/',method='POST',parms=parms,debug=debug)
        export_id = data['id']

        complete = 0
        while complete < 100:

            progress = self.api_request(call='responseexports/'+export_id,method='GET',debug=debug)
            complete = progress['percentComplete']

        download_call = 'responseexports/'+export_id+'/file'
        download_path = self.api_request(call=download_call,method='GET',export=True,debug=debug)

        data_file = download_path+'/'+os.listdir(download_path)[0]
        data = open(data_file,'r')

        return json.load(data)

########################################################################################################################
# THE UPDATE LINE
########################################################################################################################

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

    def processResponses(self,survey_object,sqlid=None,exclude=None,tags=True,debug=False):
        '''Builds a list of responses using ids (tags optional). Excludes specified fields (exclude).'''
        
        print 'Building responses list.'
        
        t0 = time.time()
        responses = []
        
        surveyid = survey_object.qid

        if sqlid is not None:
            surveyid = sqlid

        # These are all the default fields that are being excluded from the response set, because they are included in
        # the respondents table
        headers = ['ResponseID','ExternalDataReference','Name','EmailAddress','IPAddress','Status','StartDate','ResponseSet',
                    'EndDate','Finished','Score','FirstName','LastName']
        
        # if there are questions passed through the exclude parameter they will be added here
        if exclude:
            headers = headers+exclude

        # The full list of EDs to skip over (removes spaces)
        edlist = [x[1].replace(' ','') for x in survey_object.schema['ED']]
        
        for num,response in enumerate(survey_object.data.findall('Response')):
            if num == 0:
                pass
            elif (num/100.00).is_integer():
                print str(num)+' rows.'

            # This finds the responsent id and its corresponding MySQL id.
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

                    question_type = [x[2] for x in survey_object.question_key if x[1]==qid][0]
                    question_selector = [x[3] for x in survey_object.question_key if x[1]==qid][0]
                    question_subselector = [x[4] for x in survey_object.question_key if x[1]==qid][0]

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

                    # Matrix: Bipolar
                    elif (question_type == 'Matrix'
                          and question_selector == 'Biploar'):

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





