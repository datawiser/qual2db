'''

qualInterface.py

'''

import json
import time
import zipfile
import os

import requests

from qual2db.credentials import qualtrics_credentials as q_creds
from qual2db.credentials import download_directory


class QualInterface(object):
    '''The interface object for communication with the Qualtrics API.'''

    def api_request(self,call='surveys',method='GET',parms=None,export=False,debug=False):
        
        url = q_creds['baseurl']+call
        
        headers = {
        'x-api-token': q_creds['token'],
        'content-type' : 'application/json'
        }

        if parms:
            parms = json.dumps(parms)

        response = requests.request(method,url,data=parms,headers=headers)

        # if the request is marked as a data download, write it to a zip file and extract it
        if export:

            qid = call.replace('responseexports/','').replace('/file','')
            path = download_directory+qid+'_data'

            with open(path+'.zip', 'wb') as f:
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

    def getSurvey(self,qid,debug=False):
        '''Quickly creates a dictionary with basic details about a given survey.'''
        
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

        print('Downloading data.')
        data = self.api_request(call='responseexports/',method='POST',parms=parms,debug=debug)
        export_id = data['id']

        complete = 0
        while complete < 100:

            progress = self.api_request(call='responseexports/'+export_id,method='GET',debug=debug)
            complete = progress['percentComplete']
            print(complete)

        download_call = 'responseexports/'+export_id+'/file'
        download_path = self.api_request(call=download_call,method='GET',export=True,debug=debug)

        data_file = download_path+'\\'+os.listdir(download_path)[0]
        data = open(data_file,'r')

        return json.load(data)





