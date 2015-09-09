######### qual2db GUI #########
###############################

# This file contains the gui object for qual2db

# Standard python library
from Tkinter import *
import tkMessageBox

# Local modules
import config
from survey import survey
from sqlInterface import sqlInterface
from qualInterface import qualInterface
from ToolTip import ToolTip
import setup as setup

# This sets the interfaces for qual2db
global sqlList
global qualList

def getSQLList():
	'''retrieves all the surveys in MySQL'''
	global sqlSurveys
	sqlSurveys = []
	global sqlListNames
	sqlListNames = []
	sqlInterface1 = sqlInterface()
	sqlSurveyList = sqlInterface1.list_surveys()
	iterator = 0
	for each in sqlSurveyList:
		sqlSurveys.append([each[0], each[1], iterator])
		sqlListNames.append(each[1])
		iterator = iterator + 1
	return sqlSurveys


def getQualList():
	'''retrieves all the qualtrics surveys that are not in MySQL'''
	global qualSurveys
	qualSurveys = []
	global qualListNames
	qualListNames = []
	qualInterface1 = qualInterface()
	qualSurveyList = qualInterface1.listSurveys()
	qids = [x[0] for x in sqlSurveys]
	iterator = 0
	counter = 0
	checker = 0
	for each in qualSurveyList:
		if each[0] in qids:
			pass
		else:
			qualSurveys.append([each[0], each[1], iterator])
			qids.append(each[0])
			qualListNames.append(each[1])
			iterator = iterator + 1
			checker = checker + 1
	return qualSurveys


def refreshList(list):
	'''fills the listboxes with the respective survey names'''
	if list=='qual':
		qualList.delete(0,END)
		getQualList()
		fillList(qualSurveys, qualList)
	elif list=='sql':
		sqlList.delete(0,END)
		getSQLList()
		fillList(sqlSurveys, sqlList)


def fullQualList():
	'''refills the qual listbox'''
	qualEntry.delete(0, END)
	title.set('')
	descriptionBox.delete(1.0, END)
	fillList(qualSurveys, qualList)


def fullSQLList():
	'''refills the sql listbox'''
	sqlEntry.delete(0, END)
	title.set('')
	descriptionBox.delete(1.0, END)
	fillList(sqlSurveys, sqlList)


def searchSQL():
	'''searches for the given term in the SQL list'''
	searchTerm = sqlEntry.get()
	title.set('')
	descriptionBox.delete(1.0, END)
	if searchTerm == '':
		if sqlList.size() < len(sqlSurveys):
			fillList(sqlSurveys, sqlList)
		else:
			pass
	else:
		updateList(searchTerm, 'sql')


def searchQual():
	'''searches for the given term in the SQL list'''
	searchTerm = qualEntry.get()
	title.set('')
	descriptionBox.delete(1.0, END)
	if searchTerm == '':
		if qualList.size() < len(qualSurveys):
			fillList(qualSurveys, qualList)
		else:
			pass
	else:
		updateList(searchTerm, 'qual')


def searchCommand(event):
	'''binds the enter key to a search command'''
	term1 = qualEntry.get()
	term2 = sqlEntry.get()
	if term1 != '':
		searchQual()
	elif term2 != '':
		searchSQL()
	else:
		fullQualList()
		fullSQLList()


def updateList(searchTerm, list):
	'''filters the list by the inputted search term'''
	if list=='qual':
		updatedQual = []
		iterator = 0
		for eachSurvey in qualSurveys:
			if searchTerm in eachSurvey[1]:
				updatedQual.append([eachSurvey[0], eachSurvey[1], iterator])
				iterator = iterator + 1
			else:
				pass
		if len(updatedQual)==0:
			title.set("\"%s\" cannot be found in the Qualtrics Survey List" % searchTerm)
		else:
			fillList(updatedQual, qualList)
	elif list=='sql':
		updatedSQL = []
		iterator = 0
		for eachSurvey in sqlSurveys:
			if searchTerm in eachSurvey[1]:
				updatedSQL.append([eachSurvey[0], eachSurvey[1], iterator])
				iterator = iterator + 1
			else:
				pass
		if len(updatedSQL)==0:
			title.set("\"%s\" cannot be found in the SQL Survey List" % searchTerm)
		else:
			fillList(updatedSQL, sqlList)


def clearDescribe(event):
	'''when user clicks on a survey, clear the describe box and the label'''
	descriptionBox.delete(1.0, END)
	title.set('')
	status.set('')


def getQid(name, surveyList):
	'''return the qid given the survey name'''
	for each in surveyList:
		if each[1] == name:
			return each[0]
		else:
			pass


def fillList(surveys, aList):
	'''fills a listbox with survey names given a survey list and a listbox'''
	if len(surveys) == 0:
		descriptionBox.insert(END, 'Survey list is empty!\n')
		title.set('Error!')
		status.set(' ')
	else:
		aList.delete(0,END)
		iterator1 = 0
		for aSurvey in surveys:
			aList.insert(aSurvey[2], aSurvey[1])
			if (iterator1 % 2)==1:
				aList.itemconfig(iterator1, {'bg':'#f0f0ff'})
			iterator1 = iterator1 + 1


def clearSelection():
	'''Clears all of the items that are selected in each of the lists'''
	sqlList.selection_clear(0, END)
	qualList.selection_clear(0, END)


def recheck(msg):
	'''displays a messagebox as a safety measure'''
	answer = tkMessageBox.askquestion("Warning!", msg + "\nAre you sure you want to continue with this?")
	return answer


def information(msg):
	'''displays a messagebox to inform execution completion'''
	tkMessageBox.showinfo("Complete", msg)


def selection(list):
	'''returns the items that are selected'''
	try:
		selected = list.get(list.curselection()[0])
	except:
		return FALSE
	return selected


def getSurvey(surveyName):
	'''returns a survey object given the survey name'''
	if selection(sqlList):
		for each in sqlSurveys:
			if surveyName==each[1]:
				return survey(each[0])
			else:
				pass
	else:
		for each in qualSurveys:
			if surveyName==each[1]:
				return survey(each[0])
			else:
				pass


def surveyDetails(self):
	'''grabs details from survey object'''
	detail = ['Qualtrics ID: ' + self.qid, 'Owner: ' + self.owner, 'Status: ' + self.status, 'Creation: '\
			+ self.creation, 'SQL ID: ' + str(self.sqlid), 'Last Refresh: ' + str(self.refresh_date), 'Qualtrics: '
			+ str(self.qualtrics_responses), 'MySQL: ' + str(self.mysql_responses)]
	return detail


def description(surveyName):
	'''returns the survey details given a survey name'''
	s = getSurvey(surveyName)
	details = surveyDetails(s)
	return details


def describeEvent():
	'''when the describe button is pressed, call the describe method'''
	describe()


def describe():
	'''describes the surveys that are selected from the sql list'''
	descriptionBox.delete(1.0, END)
	surveyName = ''
	if selection(sqlList):
		surveyName = selection(sqlList)
		status.set("Retrieving \"%s\" information..." % surveyName)
		print "\nRetrieving %s data..." % surveyName
		statusBox.update()
		detail = description(surveyName)
		title.set(surveyName)
		descriptionBox.insert(END, '\n'.join(map(str,detail)))
		status.set(' ')
		print "Complete"
	elif selection(qualList):
		surveyName = selection(qualList)
		status.set("\nRetrieving \"%s\" information..." % surveyName)
		print "Retrieving %s data..." % surveyName
		statusBox.update()
		detail = description(surveyName)
		title.set(surveyName)
		descriptionBox.insert(END, '\n'.join(map(str,detail)))
		status.set(' ')
		print "Complete"
	else:
		descriptionBox.insert(END, 'Please select a survey!')
		title.set('Error!')
		status.set(' ')


def updateEvent():
	'''when the update button is pressed, call the update method'''
	update()


def update():
	'''Updates MySQL by adding new data from Qualtrics.'''
	surveyName = ''
	if selection(sqlList):
		surveyName = selection(sqlList)
		msg = "Do you really want to update \"%s\"?" % surveyName
		answer = recheck(msg)
		if answer=='yes':
			status.set("Updating %s..." % surveyName)
			print "\nUpdating \"%s\"..." % surveyName
			statusBox.update()
			print "\tRetrieving  \"%s\"" % surveyName
			s = getSurvey(surveyName)
			print "\tStarting update"
			s.update_sql()
			print "\tUpdate complete\n\n"
			status.set("Update complete. Retrieving survey information...")
			describe()
			status.set('')
			information("Successfully updated \"%s\"." % surveyName)
		else:
			pass
	else:
		descriptionBox.delete(1.0, END)
		descriptionBox.insert(END, 'Please select a survey from the SQL Surveys list to update.')
		title.set('Error!')
		status.set(' ')


def addEvent():
	'''when the add button is pressed, call the add method'''
	add()


def add():
	'''Adds the selected survey to MySQL.'''
	surveyName = ''
	if selection(qualList):
		surveyName = selection(qualList)
		msg = 'Are you sure you want to add \"' + surveyName + '\" to the MySQL database?'
		answer = recheck(msg)
		if answer=='yes':
			descriptionBox.delete(1.0, END)
			status.set("Adding \"%s\" to MySQL..." % surveyName)
			print "\nAdding \"%s\" to MySQL..." % surveyName
			statusBox.update()
			print "\tRetrieving  \"%s\"" % surveyName
			s = getSurvey(surveyName)
			print "\tUploading \"%s\"" % surveyName
			s.update_sql()
			print "\tUpload complete"
			status.set("Add complete. Refreshing survey lists...")
			refreshList('sql')
			refreshList('qual')
			status.set('')
			information("Successfully added \"%s\" to MySQL." % surveyName)
		else:
			pass
	else:
		descriptionBox.delete(1.0, END)
		descriptionBox.insert(END, 'Please select a survey from the Qualtrics Surveys list to add.')
		title.set('Error!')
		status.set(' ')


def overhaulEvent():
	'''Calls the overhaul method'''
	overhaul()


def overhaul():
	'''Rebuilds the MySQL schema tables (use only if the survey schema has changed).'''
	surveyName = ''
	if selection(sqlList):
		msg = 'Use only if the survey schema has changed!'
		answer1 = recheck(msg)
		surveyName = selection(sqlList)
		if answer1=='yes':
			descriptionBox.delete(1.0, END)
			msg1 = 'Are you really sure you want to overhaul \"%s\"?' % surveyName
			answer = recheck(msg1)
			if answer=='yes':
				status.set("Overhauling \"%s\"..." % surveyName)
				print "\nOverhauling \"%s\"..." % surveyName
				statusBox.update()
				print "\tRetrieving \"%s\"" % surveyName
				s = getSurvey(surveyName)
				print "\tOverhauling \"%s\"" % surveyName
				s.overhaul()
				print "\tOverhaul complete"
				status.set("Overhaul complete. Retrieving survey information...")
				describe()
				status.set('')
				information("Successfully overhauled \"%s\"." % surveyName)
			else:
				pass
		else:
			pass
	else:
		descriptionBox.delete(1.0, END)
		descriptionBox.insert(END, 'Please select a survey from the SQL Surveys list.')
		title.set('Error!')
		status.set(' ')


def clearDataEvent():
	'''calls the clear data method'''
	clearData()


def clearData():
	'''Clears out all the selected survey's Respondents, and Responses in MySQL.'''
	surveyName = ''
	if selection(sqlList):
		surveyName = selection(sqlList)
		msg = 'Do you want to clear out all of \"%s\" Respondents, and Responses from MySQL?' % surveyName
		answer = recheck(msg)
		if answer=='yes':
			descriptionBox.delete(1.0, END)
			status.set("Clearing \"%s\" data from MySQL..." % surveyName)
			print "\nClearing data from \"%s\"..." % surveyName
			statusBox.update()
			print "\tRetrieving \"%s\"" % surveyName
			s = getSurvey(surveyName)
			print "\tClearing \"%s\" data" % surveyName
			s.clear_data()
			print "\tClear data complete"
			status.set("Clear Data complete. Retrieving survey information...")
			describe()
			status.set('')
			information("Successfully cleared out all of \"%s\" Respondents and Responses from MySQL." % surveyName)
		else:
			pass
	else:
		descriptionBox.delete(1.0, END)
		descriptionBox.insert(END, 'Please select a survey from the SQL Surveys list.')
		title.set('Error!')
		status.set(' ')


def removeEvent():
	'''calls the remove method'''
	remove()


def remove():
	'''Removes the survey, its schema and data, from MySQL.'''
	surveyName = ''
	if selection(sqlList):
		surveyName = selection(sqlList)
		msg = 'Do you want to remove \"%s\" from the MySQL database?' % surveyName
		answer = recheck(msg)
		if answer=='yes':
			descriptionBox.delete(1.0, END)
			status.set("Removing \"%s\" from MySQL..." % surveyName)
			print "\nRemoving %s from MySQL..." % surveyName
			statusBox.update()
			print "\tRetrieving %s" % surveyName
			s = getSurvey(surveyName)
			print "\tRemoving %s" % surveyName
			s.remove()
			print "\tRemove complete"
			status.set("Remove complete. Refreshing survey lists...")
			refreshList('sql')
			refreshList('qual')
			status.set('')
			information("Successfully removed \"%s\" from MySQL." % surveyName)
		else:
			pass
	else:
		descriptionBox.delete(1.0, END)
		descriptionBox.insert(END, 'Please select a survey from the SQL Surveys list.')
		title.set('Error!')
		status.set(' ')


def reconfigure():
	'''Closes the gui and opens the setup menu'''
	app.quit()
	app.destroy()
	setup.main()


def main():
	global app
	print "Openning Qual2DB App..."
	app = Tk()
	app.title("qual2db")
	
	'''leftFrame displays the list of surveys that are in Qualtrics'''
	print "\tConfiguring the interface"
	leftFrame = Frame(app)
	leftFrame.pack(side=LEFT, pady=5, padx=5, fill=BOTH, expand=TRUE)
	#qualListLabel creates a title for the list
	qualListLabel = Button(leftFrame, font="Arial 14 bold", text="Qualtrics Surveys", command=fullQualList)
	qualListLabel.pack(side=TOP, fill=X)
	qualListToolTip = ToolTip(qualListLabel, "Refreshes the Qualtrics Survey List.")
	#scrollbarQualY creates a vertical scrollbar for the Qualtrics list
	scrollbarQualY = Scrollbar(leftFrame)
	# qualSearchButton.config(image=filterPic, height="20", width="20")
	qualSearchTerm = StringVar()
	qualSearchTerm = ''
	#searchbar for qualList
	#retrieve survey names
	# getSQLList()
	# getQualList()
	# qualEntry = AutocompleteEntry(qualListNames, leftFrame, textvariable=qualSearchTerm, width=45, listboxFrame="leftFrame")
	global qualEntry
	qualEntry = Entry(leftFrame, textvariable=qualSearchTerm, width=45)
	#searchButton for search bar
	global qualSearchButton
	qualSearchButton = Button(qualEntry, text="Search", height = 1, font="arial 6", command=searchQual)
	#fullQualButton fill the qualtrics survey list
	clearQualButton = Button(qualEntry, text="Clear ", height = 1, font="arial 6", command=fullQualList)
	#scrollbarQualX creates a horizontal scrollbar for the Qualtrics list
	scrollbarQualX = Scrollbar(leftFrame, orient=HORIZONTAL)
	#qualList creates a listbox that lists the qual surveys
	global qualList
	qualList = Listbox(leftFrame, width=45, yscrollcommand=scrollbarQualY.set, xscrollcommand=scrollbarQualX.set)
	#pack and configure the scrollbars
	scrollbarQualY.pack(side=RIGHT, fill=Y)
	scrollbarQualX.pack(side=BOTTOM, fill=X)
	scrollbarQualY.config(command=qualList.yview)
	scrollbarQualX.config(command=qualList.xview)
	qualEntry.pack(side=TOP, fill=X)
	clearQualButton.pack(side=RIGHT, fill=X)
	qualSearchButton.pack(side=RIGHT)

	'''centerFrame lists the functions as buttons and has
		a window for listing the descriptions of a survey'''
	centerFrame = Frame(app)
	centerFrame.pack(side=LEFT, pady=5, padx=5, fill=BOTH, expand=TRUE)
	#emptyBox is a label that just takes up space
	emptyBox = Label(centerFrame, height=5, text='')
	emptyBox.pack(side=TOP, fill=X, pady=5)
	print "\tCreating interface buttons"
	#"Survey" updates the sql survey
	update = Button(centerFrame, text="Update", width=10, font="Verdana 12", command=updateEvent)
	update.pack(side=TOP, pady=10)
	updateToolTip = ToolTip(update, "Updates a SQL survey.\nClick on a survey from the SQL Survey list.")
	#"Add" adds a qualtrics survey
	add = Button(centerFrame, text="Add", width=10, font="Verdana 12", command=addEvent)
	add.pack(side=TOP, pady=10)
	addToolTip = ToolTip(add, "Adds a Qualtrics survey to the MySQL.\nClick on a survey from the Qualtrics Survey list.")
	#overhaul
	overhaul = Button(centerFrame, text="Overhaul", width=10, font="Verdana 12", command=overhaulEvent)
	overhaul.pack(side=TOP, pady=10)
	overhaulToolTip = ToolTip(overhaul, "Rebuilds the MySQL schema tables (use only if the survey schema has changed).\nClick on a survey from the SQL Survey list.")
	#clear data
	clear = Button(centerFrame, text="Clear Data", width=10, font="Verdana 12", command=clearDataEvent)
	clear.pack(side=TOP, pady=10)
	clearToolTip = ToolTip(clear, "Clears out all of the selected survey's Respondents, and Responses in MySQL.\nClick on a survey from the SQL Survey list.")
	#remove
	remove = Button(centerFrame, text="Remove", width=10, font="Verdana 12", command=removeEvent)
	remove.pack(side=TOP, pady=10)
	removeToolTip = ToolTip(remove, "Removes the selected survey's schema and data from MySQL.\nClick on a survey from the SQL Survey list.")
	#unselect
	deselect = Button(centerFrame, text="Deselect All", width=10, font="Verdana 12", command=clearSelection)
	deselect.pack(side=TOP, pady=10)
	deselectToolTip = ToolTip(deselect, "Unselects all highlighted surveys from the survey lists.")
	#describe button describes the selected survey
	describe = Button(centerFrame, text='Describe', width=10, font='Verdana 12', command=describeEvent)
	describe.pack(side=TOP, pady=10)
	describeToolTip = ToolTip(describe, "Displays the survey information.")
	#loadingBox is a label that displays the status of the load
	loading = StringVar()
	loadingBox = Label(centerFrame, textvariable=loading, font=("times 10"))
	loading.set(' ')
	loadingBox.pack(side=TOP, fill=X, pady=10)
	#statusBox is a label that displays the status
	global status
	status = StringVar()
	global statusBox
	statusBox = Label(centerFrame, width=50, textvariable=status, anchor=W, font=("times 11"))
	status.set(' ')
	statusBox.pack(side=TOP, fill=X, pady=20)
	# reconfigurebutton is a button that lets the user configure the connections
	reconfigureButton = Button(centerFrame, text="Reconfigure", font="Verdana 12", bd=3, command=reconfigure)
	reconfigureButton.pack(side=BOTTOM, fill=X)
	reconfigureToolTip = ToolTip(reconfigureButton, "Reconfigure your Qualtrics and SQL Connections.")
	#descriptionBox is a textbox that describes the chosen survey
	global descriptionBox
	descriptionBox = Text(centerFrame, height=10, width=35, font="times  10")
	# descriptionBox.config(state=ENABLED)
	descriptionBox.pack(side=BOTTOM, pady=10, fill=BOTH)
	#namelabel is the name of the survey
	global title
	title = StringVar()
	title.set('Welcome to Qual2DB')
	nameLabel = Label(centerFrame, textvariable=title, font=("arial 10 bold"))
	nameLabel.pack(side=BOTTOM, fill=X)

	'''rightframe displays the list of surveys in the SQL database'''
	rightFrame = Frame(app)
	rightFrame.pack(side=LEFT, pady=5, padx=5, fill=BOTH,expand=TRUE)
	#sqlListLabel creates a title for the list
	sqlListLabel = Button(rightFrame, font="Arial 14 bold", text="SQL Surveys", command=fullSQLList)
	sqlListLabel.pack(side=TOP, fill=X)
	sqlListToolTip = ToolTip(sqlListLabel, "Refreshes the SQL Survey List.")
	#scrollbarSQLY creates a vertical scrollbar for the SQL list
	scrollbarSQLY = Scrollbar(rightFrame)
	#searchbar for sqlList
	sqlSearchTerm = StringVar()
	sqlSearchTerm = ''
	global sqlEntry
	sqlEntry = Entry(rightFrame, textvariable=sqlSearchTerm, width=45)
	#searchButton for search bar
	global sqlSearchButton
	sqlSearchButton = Button(sqlEntry, text="Search", height = 1, font="arial 6", command=searchSQL)
	app.bind('<Return>', searchCommand)
	#fullSQLButton fill the SQL survey list
	clearSQLButton = Button(sqlEntry, text="Clear ", height = 1, font="arial 6", command=fullSQLList)
	#scrollbarSQLX creates a horizontal scrollbar for the SQL list
	scrollbarSQLX = Scrollbar(rightFrame, orient=HORIZONTAL)
	#sqlList creates a listbox that lists the sql surveys
	global sqlList
	sqlList = Listbox(rightFrame, width=45, yscrollcommand=scrollbarSQLY.set, xscrollcommand=scrollbarSQLX.set)
	#pack and configure the scrollbar
	scrollbarSQLY.pack(side=RIGHT, fill=Y)
	scrollbarSQLY.config(command=sqlList.yview)
	scrollbarSQLX.pack(side=BOTTOM, fill=X)
	scrollbarSQLX.config(command=sqlList.xview)
	sqlEntry.pack(side=TOP, fill=X)
	sqlEntry.focus()
	clearSQLButton.pack(side=RIGHT, fill=X)
	sqlSearchButton.pack(side=RIGHT)
	#grab the sql surveys and print them on the listbox(sqlList)
	sqlList.pack(side=LEFT, fill=BOTH, expand=TRUE)
	print "\tDownloading SQL data"
	refreshList('sql')
	sqlList.bind("<Button-1>", clearDescribe)
	#grab the qualtrics surveys and print them on the listbox(qualList)]
	qualList.pack(side=LEFT, fill=BOTH, expand=TRUE)
	print "\tDownload Qualtrics data"
	refreshList('qual')
	qualList.bind("<Button-1>", clearDescribe)
	print "\tComplete"
	app.mainloop()
	print "\tQual2DB Open"

if __name__=='__main__':
	'''runs the app'''
	main()
