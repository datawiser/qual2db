# qual2db
A python package that pulls survey data from [Qualtrics](http://www.qualtrics.com/) and transforms it into a multi-table relational database (Surveys, Blocks, Questions, Choices, Answers, Respondents, Responses). Originally designed to replicate the useful data structure provided by the Inquisite survey system.

### Example
    import qual2db
    
    s = qual2db.survey('{your survey id}')
    s.update_sql()
    
    sdf
