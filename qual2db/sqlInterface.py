##### MySQL Interface #####
###########################

# This file contains the SQL-interface object and all the functions
# that it uses to interface with the MySQL database

# MySQL connector
import mysql.connector as sql

# Standard python library
import datetime
from dateutil import parser
import time

# Local modules
import config


class sqlInterface(object):
    """The interface object for communicating with MySQL."""

    def __init__(self):
        """Initializes the interface with a new MySQL connection."""

        try:
            self.cnx.close()
        except:
            self.cnx = None

        cnx = sql.connect(
            user=config.sqlUser,
            passwd=config.sqlPassword,
            host=config.sqlHost,
            db=config.sqlDB
        )

        self.cnx = cnx

    ####################################################################
    # Functions for querying and managing MySQL data
    ####################################################################

    def list_surveys(self):
        """Lists all the surveys currently stored in MySQL."""
        cur = self.cnx.cursor()
        qry = ('SELECT survey_id,survey_qid,name FROM surveys')

        cur.execute(qry)
        result = cur.fetchall()

        return result

    def get_survey_id(self, survey_qid):
        """Checks if a survey exists in SQL. If so, the MySQL id is returned."""

        cur = self.cnx.cursor()
        cur.execute('SELECT survey_id '
                    'FROM surveys '
                    'WHERE survey_qid = "' + str(survey_qid) + '"')
        try:
            survey_id = cur.fetchone()[0]
        except:
            return False

        return survey_id

    def get_refresh_date(self, survey_id):
        """Gets the date a survey was last refreshed."""
        cur = self.cnx.cursor()

        qry = ('SELECT last_refresh FROM surveys '
               'WHERE survey_id=' + str(survey_id))
        cur.execute(qry)
        last_refresh = cur.fetchone()[0]

        return last_refresh

    def upload_survey(self, survey):
        """Adds (or updates) a survey given a survey object. Returns the MySQL id."""

        cur = self.cnx.cursor()
        survey_id = self.get_survey_id(survey.qid)

        print 'WHERE survey_id="' + str(survey_id) + '";'

        if survey_id:
            qry = ('UPDATE surveys SET '
                   'name="' + survey.attributes['name'] + '",'
                   'isActive="' + str(survey.attributes['isActive']) + '",'
                   'endDate="' + survey.attributes['endDate'] + '",'
                   'startDate="' + survey.attributes['startDate'] + '",'
                   'auditableResponses="' +
                   str(survey.attributes['auditableResponses']) + '",'
                   'deletedResponses="' +
                   str(survey.attributes['deletedResponses']) + '",'
                   'generatedResponses="' +
                   str(survey.attributes['generatedResponses']) + '",'
                   'lastModifiedDate="' +
                   survey.attributes['lastModifiedDate'] + '" '
                   'WHERE survey_id="' + str(survey_id) + '";')

            data = survey.attributes

            cur.execute(qry, data)
            self.cnx.commit()

            return survey_id

        else:

            qry = ('INSERT INTO surveys ('
                   'survey_qid, '
                   'name, '
                   'ownerId, '
                   'isActive, '
                   'creationDate, '
                   'endDate, '
                   'startDate, '
                   'auditableResponses, '
                   'deletedResponses, '
                   'generatedResponses, '
                   'lastModifiedDate) '
                   'VALUES ('
                   '%(survey_qid)s, '
                   '%(name)s, '
                   '%(ownerId)s, '
                   '%(isActive)s, '
                   '%(creationDate)s, '
                   '%(endDate)s, '
                   '%(startDate)s, '
                   '%(auditableResponses)s, '
                   '%(deletedResponses)s, '
                   '%(generatedResponses)s, '
                   '%(lastModifiedDate)s '
                   ')')

            data = survey.attributes

            cur.execute(qry, data)
            self.cnx.commit()
            survey_id = get_survey_id(survey.qid)

            return survey_id
