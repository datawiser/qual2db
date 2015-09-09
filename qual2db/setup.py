########### qual2db ########### 
############################### 

# This file contains the setup object for qual2db

# Standard python library
from Tkinter import *
import tkMessageBox
import urllib2
import urllib
import os
import ConfigParser

# Local modules
from ToolTip import ToolTip
import thegui as thegui

# MySQL python connector. Exits if it is not installed.
try:
    import mysql.connector as sql
except:
    print 'Error: No Python-MySQL ODBC driver found.'
    print 'Install with: R:\CSR\Admin\Computing\Software\MySQL\mysql-connector-python-2.0.3-py2.7.msi'
    print '-'*30
    raw_input('press any key to exit')
    sys.exit()

global qualConnection, sqlConnection, guiOn
qualConnection = False
sqlConnection = False
guiOn = False

package_directory = os.path.dirname(__file__)
config_file = os.path.join(package_directory, 'config.ini')

Config = ConfigParser.ConfigParser()
Config.read(config_file)


def setQual():
    '''set the qualtrics credentials with the given values'''
    baseurlInput = baseurlEntry.get()
    userInput = userEntry.get()
    passwordInput =qualpasswordEntry.get()
    tokenInput = tokenEntry.get()
    versionInput = versionEntry.get()
    Config.set('Qualtrics Credentials', 'baseurl', baseurlInput)
    Config.set('Qualtrics Credentials', 'User', userInput)
    Config.set('Qualtrics Credentials', 'Password', passwordInput)
    Config.set('Qualtrics Credentials', 'Token', tokenInput)
    Config.set('Qualtrics Credentials', 'Version', versionInput)
    with open('config_test.ini', 'w') as configfile:
        Config.write(configfile)
    testQual()


def setSQL():
    '''set the SQL credentials with the given values'''
    sqlUser = sqluserEntry.get()
    sqlPassword = sqlpasswordEntry.get()
    sqlHost =sqlHostEntry.get()
    sqlDB = sqlDBEntry.get()
    Config.set('MySQL Credentials', 'sqlUser', sqlUser)
    Config.set('MySQL Credentials', 'sqlPassword', sqlPassword)
    Config.set('MySQL Credentials', 'sqlHost', sqlHost)
    Config.set('MySQL Credentials', 'sqlDB', sqlDB)
    with open('config_test.ini', 'w') as configfile:
        Config.write(configfile)
    testSQL()


def qualCredentials(frame):
    '''creates the form for qualtrics'''
    qualCredential = Label(frame, text="Qualtrics Credentials", font="Verdana 14")
    qualCredential.pack(side=TOP, fill=X, pady=3)
    leftFrame = Frame(frame)
    leftFrame.pack(side=LEFT)
    rightFrame = Frame(frame)
    rightFrame.pack(side=LEFT)
    baseurlLabel = Label(leftFrame, bd=2, text="Baseurl:")
    baseurlLabel.pack(side=TOP, pady=3)
    userLabel = Label(leftFrame, bd=2, text="User:")
    userLabel.pack(side=TOP, pady=3)
    passwordLabel = Label(leftFrame, bd=2, text="Password:")
    passwordLabel.pack(side=TOP, pady=3)
    tokenLabel = Label(leftFrame, bd=2, text="Token:")
    tokenLabel.pack(side=TOP, pady=3)
    versionLabel = Label(leftFrame, bd=2, text="Version:")
    versionLabel.pack(side=TOP, pady=3)
    global baseurlEntry, userEntry, qualpasswordEntry, tokenEntry, versionEntry
    baseurlEntry = Entry(rightFrame, bd=2, width=25)
    baseurlEntry.pack(side=TOP, padx=3, pady=3)
    userEntry = Entry(rightFrame, bd=2, width=25)
    userEntry.pack(side=TOP, pady=3)
    qualpasswordEntry = Entry(rightFrame, bd=2, show="*", width=25)
    qualpasswordEntry.pack(side=TOP, pady=3)
    tokenEntry = Entry(rightFrame, bd=2, width=25)
    tokenEntry.pack(side=TOP, pady=3)
    versionEntry = Entry(rightFrame, bd=2, width=25)
    versionEntry.pack(side=TOP, pady=3)
    bottomFrame = Frame(frame)
    bottomFrame.pack(side=RIGHT)
    qualTestButton = Button(bottomFrame, text="Test", font="Verdana 12", width=7, bd=3, command=setQual)
    qualTestButton.pack(side=BOTTOM, padx=10, pady=6)


def sqlCredentials(frame):
    '''creates the form for SQL'''
    sqlCredential = Label(frame, text="MySQL Credentials", font="Verdana 14")
    sqlCredential.pack(side=TOP, fill=X, pady=3)
    leftFrame = Frame(frame)
    leftFrame.pack(side=LEFT)
    rightFrame = Frame(frame)
    rightFrame.pack(side=LEFT)
    userLabel = Label(leftFrame, bd=2, text="User:")
    userLabel.pack(side=TOP, pady=3)
    sqlPasswordLabel = Label(leftFrame, bd=2, text="Password:")
    sqlPasswordLabel.pack(side=TOP, pady=3)
    sqlHostLabel = Label(leftFrame, bd=2, text="sqlHost:")
    sqlHostLabel.pack(side=TOP, pady=3)
    sqlDBLabel = Label(leftFrame, bd=2, text="sqlDB:")
    sqlDBLabel.pack(side=TOP, pady=3)
    global sqluserEntry, sqlpasswordEntry, sqlHostEntry, sqlDBEntry 
    sqluserEntry = Entry(rightFrame, bd=2, width=25)
    sqluserEntry.pack(side=TOP, pady=3)
    sqlpasswordEntry = Entry(rightFrame, bd=2, show="*", width=25)
    sqlpasswordEntry.pack(side=TOP, pady=3)
    sqlHostEntry = Entry(rightFrame, bd=2, width=25)
    sqlHostEntry.pack(side=TOP, pady=3)
    sqlDBEntry = Entry(rightFrame, bd=2, width=25)
    sqlDBEntry.pack(side=TOP, pady=3)
    bottomFrame = Frame(frame)
    bottomFrame.pack(side=RIGHT)
    sqlTestButton = Button(bottomFrame, text="Test", font="Verdana 12", width=7, bd=3, command=setSQL)
    sqlTestButton.pack(side=BOTTOM, padx=10, pady=6)


def startTheGui():
    '''starts the GUI if we are able to connect to both the SQL server and Qualtrics'''
    if (sqlConnection & qualConnection):
        if (guiOn):
            try:
                global setupApp
                setupApp.quit()
                setupApp.destroy()
            except:
                pass
        else:
            pass
        try:
            thegui.main()
        except:
            print "Unable to open thegui"
    else:
        pass


def testQual():
    '''Tests the qualtrics connection when the test button is pressed'''
    try:
        initialTestQual()
        if qualConnection:
            information("Connected to Qualtrics")
        else:
            pass
    except:
        print "Unable to connect to Qualtrics."
        print "Please try again."


def testSQL():
    '''Tests the SQL connection when the test button is pressed'''
    try:
        initialTestSQL()
        if sqlConnection:
            information("Connected to MySQL")
        else:
            pass
    except:
		print "Unable to connect to MySQL."
		print "Please try again."


def information(msg):
    '''displays messagebox to inform execution completion'''
    tkMessageBox.showinfo("Success", msg)


def initialTestQual():
    '''Tests the Qualtrics connection'''
    try:
        baseurl = Config.get('Qualtrics Credentials','baseurl')
        User = Config.get('Qualtrics Credentials','User')
        Password = Config.get('Qualtrics Credentials','Password')
        Token = Config.get('Qualtrics Credentials','Token')
        Version = Config.get('Qualtrics Credentials','Version')
        payload = {'Request':'getSurveys', 'SurveyID': None,'Format':'XML','Password':Password,
                   'Token':Token,'Version':Version,'User':User, 'ExportQuestionIDs':'1'}
        request = urllib2.Request(baseurl, urllib.urlencode(payload))
        response = urllib2.urlopen(request)
        global qualConnection
        qualConnection = True
    except:
        print "Unable to connect to Qualtrics."


def initialTestSQL():
    '''Tests the SQL connection'''
    try:
        sqlUser = Config.get('MySQL Credentials','sqlUser')
        sqlPassword = Config.get('MySQL Credentials','sqlPassword')
        sqlHost = Config.get('MySQL Credentials','sqlHost')
        sqlDB = Config.get('MySQL Credentials','sqlDB')
        try:
            cnx.close()
        except:
            cnx = None
        cnx = sql.connect(user = sqlUser, password = sqlPassword, host = sqlHost, database = sqlDB)
        global sqlConnection
        sqlConnection = True
    except:
        print "Unable to connect to MySQL."


def main():
    global setupApp
    setupApp = Tk()
    setupApp.title("Qual2DB Setup")
    
    titleFrame = Frame(setupApp)
    titleFrame.pack(side=TOP)
    title = Label(titleFrame, text="Qual2DB Setup", font="Verdana 16 bold")
    title.pack(side=TOP)
    
    qualFrame = Frame(setupApp)
    qualFrame.pack(side=TOP)
    if (qualConnection):
        pass
    else:
        qualCredentials(qualFrame)
    sqlFrame = Frame(setupApp)
    sqlFrame.pack(side=TOP)
    if (sqlConnection):
        pass
    else:
        sqlCredentials(sqlFrame)
    buttonFrame = Frame(setupApp)
    buttonFrame.pack(side=TOP)
    connectButton = Button(buttonFrame, text="Connect", font="Verdana 12", width=7, bd=3, command=startTheGui)
    connectButton.pack(side=RIGHT, padx=10, pady=6)
    print "Openning Qual2DB Setup App..."
    global guiOn
    guiOn = True
    setupApp.mainloop()


def run():
    '''checks the connection and starts the program'''
    try:
        initialTestQual()
        initialTestSQL()
    except:
        pass
    if (sqlConnection == False or qualConnection == False):
        main()
    else:
        print "Connected to Qualtrics"
        print "Connected to SQL"
        startTheGui()

if __name__ == '__main__':
    run()
