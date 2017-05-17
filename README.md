# qual2db
A python package that pulls survey data from [Qualtrics](http://www.qualtrics.com/) and transforms it in to a multi-table relational database (Surveys, Blocks, Questions, Choices, Answers, Respondents, Responses).

## Start
*revise*

### Command Line Tips
If using as a library, here is an example of how to run qual2db:

    from qual2db import Manager
    
    manager = Manager('sample.db')
    survey = manager.add_survey('SV_YOURSURVEYID')

See the [wiki](https://github.com/calvincsr/qual2db/wiki) for complete documentation.
