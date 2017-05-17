
import os
import qual2db

from qual2db.datamodel import Survey, Block, Question, SubQuestion
from qual2db.manager import data_mapper, schema_mapper, entity_mapper, build_index, parse_responses

try:
    os.remove('sample.db')
except:
    pass

db = qual2db.Database('sample')
qi = qual2db.QualInterface()

schema = qi.getSurvey('SV_03xFTFmDEiceCP3')
data = qi.getData('SV_03xFTFmDEiceCP3')

s = Survey()
schema_mapper(s, schema)
db.save(s)

index = build_index(s, schema)
parse_responses(s, schema, data)

db.save(s)
