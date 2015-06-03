# qual2db
A python package that pulls survey data from [Qualtrics](http://www.qualtrics.com/) and transforms it in to a multi-table relational database (Surveys, Blocks, Questions, Choices, Answers, Respondents, Responses).

### Example

    import qual2db
    
    s = qual2db.survey('{your survey id}')
    s.update_sql()

See the [wiki](https://github.com/calvincsr/qual2db/wiki) for complete documentation.
