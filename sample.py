
import os
from qual2db import Manager

try:
    os.remove('sample.db')
except:
    pass

m = Manager('sample.db')
m.listSurveys()
s = m.add_survey('SV_03xFTFmDEiceCP3')


"""

add_survey()
remove_survey()
truncate()

"""
