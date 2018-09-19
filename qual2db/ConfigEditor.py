import os
import datetime
import configparser
from configparser import ConfigParser

module_directory = os.path.dirname(__file__)

root1,tail1 = os.path.split(module_directory)

print(root1)

config_file_dir = os.path.join(module_directory, 'config.ini')
config = configparser.SafeConfigParser()
config.read(config_file_dir)

databases = ['MySQL','SQLite']

def sqlite_name_generator(root=root1,name='test'):

    now = datetime.datetime.now()
    name = r'\qual2db\databases\test'
    date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
    constr = r'sqlite:///'+ root + name + date_time + '.db?check_same_thread=False?charset=utf8'

    return(constr)

sections = {
    'SQLite':{'section':'SQLite_Credentials','constr':sqlite_name_generator()},
    'MySQL':{'section':'MySQL_Credentials','constr':'mysql+pymysql://csr:ministryoffunnywalks@upshot.calvin.edu/csr_qual2db_3'}
    }

def config_editor(databases=['SQLite']):
    r''' This functions edits the config.ini file 
    '''

    for section in sections:
        if section in databases:
            if config.has_section(sections[section]['section']):
                if len(config.get(sections[section]['section'],'constr')) == 0:
                       pass
                else:
                    config.remove_option(sections[section]['section'],'constr')
                    config.set(sections[section]['section'],'constr',sections[section]['constr'])

            else:
                config.add_section(sections[section]['section'])
                config.set(sections[section]['section'],'constr',sections[section]['constr'])
        else:
            pass
        with open(config_file_dir,'w') as file:
            config.write(file)

            
