# qual2db 2.0
A python package that pulls survey data from [Qualtrics](http://www.qualtrics.com/) and transforms it in to a multi-table relational database (Surveys, Blocks, Questions, Choices, Answers, Respondents, Responses).

If using as a library, here is an example of how to run qual2db:

    from qual2db.manager import SurveyManager

    manager = SurveyManager()
    manager.add_survey('SV_YOURSURVEYID')

To use the browser cherrypy powered gui run this from the command line:

from qual2db.manager import SurveyManager

    python start-gui.py
