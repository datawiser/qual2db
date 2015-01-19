# qual2db
Qual2DB is a python package that puts [Qualtrics](http://www.qualtrics.com/) survey data into a multi-table relational database (Surveys, Questions, Choices, Answers, Respondents, Responses). Qual2DB was designed to replicate the useful data structure provided by the Inquisite survey system. Qual2DB can be used as a python-package, command-line tool or with a simple HTML interface (experimental).

### Example
    import qual2db
    
    s = qual2db.survey.Survey('{your survey id}')
    s.align_with_sql()
    s.update_mysql()
