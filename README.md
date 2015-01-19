# qual2db
Python package that puts [Qualtrics](http://www.qualtrics.com/) survey data into a multi-table relational database (Surveys, Questions, Choices, Answers, Respondents, Responses). Designed to replicate the useful data structure provided by the Inquisite survey system

### Example
    import qual2db
    
    s = qual2db.survey.Survey('{your survey id}')
    s.align_with_sql()
    s.update_mysql()
