# qual2db
A python package that pulls survey data from [Qualtrics](http://www.qualtrics.com/) and transforms it in to a multi-table relational database (Surveys, Blocks, Questions, Choices, Answers, Respondents, Responses).

## Start
To get started, download the files and run setup.py to configure the connections to both MySQL and Qualtrics.


### Command Line Tips
If using as a library, here is an example of how to run qual2db:

    import qual2db
    
    s = qual2db.survey('{your survey id}')
    s.update_sql()

See the [wiki](https://github.com/calvincsr/qual2db/wiki) for complete documentation.
