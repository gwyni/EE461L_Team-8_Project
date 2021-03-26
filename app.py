from flask import Flask, render_template,url_for, request, redirect, session
from flask_pymongo import PyMongo
import numbers
app = Flask(__name__)

error_messages= {1:'Input is not a number', 2:'Request must be greater than 0', 3: 'Request is greater than availability', 4: 'Successfully checked out resources'}

# this is the url and variables for the user databse, wehen accessing the database use the "userDb" variable
#app.config["MONGO_URI"] = 'mongodb+srv://mainUser:TahoeMontecito!@461l-team8.lchei.mongodb.net/myDb?retryWrites=true&w=majority'
mongo = PyMongo(app,uri='mongodb+srv://mainUser:TahoeMontecito!@461l-team8.lchei.mongodb.net/myDb?retryWrites=true&w=majority')
userDb = mongo.db.users

# this is the url and variables for the project databse, wehen accessing the database use the "projectDb" variable
#app.config["MONGO_URI2"] = 'mongodb+srv://mainUser:TahoeMontecito!@461l-team8.lchei.mongodb.net/storedProjects?retryWrites=true&w=majority'
mongo2 = PyMongo(app,uri='mongodb+srv://mainUser:TahoeMontecito!@461l-team8.lchei.mongodb.net/storedProjects?retryWrites=true&w=majority')
projectDb = mongo2.db.projects

# this is the url and variables for the project databse, wehen accessing the database use the "projectDb" variable
#app.config["MONGO_URI3"] = 'mongodb+srv://mainUser:TahoeMontecito!@461l-team8.lchei.mongodb.net/hardware?retryWrites=true&w=majority'
mongo3 = PyMongo(app,uri='mongodb+srv://mainUser:TahoeMontecito!@461l-team8.lchei.mongodb.net/hardware?retryWrites=true&w=majority')
hwDb = mongo3.db.hardwareSets

app.secret_key = b'5tei3of8g5rg3i/'

# prints out the contents of a database
def printDatabase(database):
	# you have to have the curly braces
	elements = database.find({})
	print(elements)
	for element in elements:
		print(element)

# returns true if a username has already been used by another user, false otherwise
def userNameAlreadyExists(database,username):
	if database.find_one({"username":username}) == None:
		return False
	else:
		return True

# returns true if a password has already been used by another user, false otherwise
def passwordAlreadyExists(database,password):
	if database.find_one({"password":password}) == None:
		return False
	else:
		return True

# returns true if an inputted password matches the username, returns False otherwise
def passwordMatches(database,username,password):
	userFound = database.find_one({"username":username})
	print(userFound["password"])
	if(userFound["password"] == password):
		return True
	return False

# returns true if a project name already exists
def projectNameAlreadyExists(database,name):
	if database.find_one({"Project Name":name}) == None:
		return False
	else:
		return True


# just have a / means that's the home page
@app.route('/',methods=['GET','POST'])
def login():
	invalidName = False
	invalidPassword = False
	# if we have submitted a form
	message = ""
	if(request.method=='POST'):
		# loginInfo is a dictionary that contains as keys the names of the input fields in the form group and the actual user input as values
		loginInfo = request.form
		# check if the username or password fields are empty
		username = loginInfo.get('username')
		password = loginInfo.get('password')
		if not loginInfo.get('username'):
			invalidName = True
		if not loginInfo.get('password'):
			invalidPassword = True
		# username is empty
		if(invalidName and not invalidPassword):
			message = 'Empty Username!'
			#return render_template('userLoginPage.html',content='Empty Username!')
		# password is empty
		elif(not invalidName and invalidPassword):
			message  = 'Empty Password!'
			#return render_template('userLoginPage.html',content='Empty Password!')
		# both invalid
		elif(invalidName and invalidPassword):
			message = 'Empty Username and Password!'
			#return render_template('userLoginPage.html',content='Empty Username and Password!')
		# both have possibly valid entries
		else:
			# if the login button has been pressed
			if request.form.get('login'):
				# if a username has already been used, check to see if the correct password has been entered
				if userNameAlreadyExists(userDb,username):
				 	if passwordMatches(userDb,username,password):
				 		session['username'] = username
				 		return redirect(url_for('userPortal'))
				 	else:
				 		message = 'Incorrect username and password!'

				#return render_template('userLoginPage.html',content='A user already has that username!')
			# elif not userNameAlreadyExists(userDb,username) and passwordAlreadyExists(userDb,password):
			# 	message = 'A user already has that password!'
			# 	#return render_template('userLoginPage.html',content='A user already has that password!')
			# # if a username and password are both already in the database
			# elif userNameAlreadyExists(userDb,username) and passwordAlreadyExists(userDb,password):
			# 	message = 'That username and password have already been used!'
				#return render_template('userLoginPage.html',content='That username and password have already been used!')

			# if the Sign Up button has been pressed
			if request.form.get('signUp'):
				# if the the inputted username has not already been used, add username and password to the database
				if not userNameAlreadyExists(userDb,username):
					userDb.insert_one({"username":loginInfo.get('username'), "password":loginInfo.get('password')})
					session['username'] = username
					#print(session['username'])
					#return render_template('userPortal.html')
					return redirect(url_for('userPortal'))
				else:
					message = 'That user name has already been used!'
		#return redirect(request.url)
	return render_template('userLoginPage.html',content=message)

def validCheckoutInput(requested, available):
	if not isinstance(requested,numbers.Number):
		return 1		# Error 1: request must be an integer
	elif(requested<=0):
		return 2		# Error 2: request must be greater than 0
	elif(requested>available):
		return 3 		# Error 3: requested too many resources
	return 4			# no error

# below displays the HTML for the user portal page

@app.route('/userPortal',methods=['GET','POST'])
def userPortal():
	projectMsg = ""
	displayUser = ""
	projectManageMsg=""
	if 'username' in session:
			displayUser = session['username']
	if(request.method=='POST'):
		resourcesInfo = request.form
		projectName = resourcesInfo.get('project name')

		# if the submit button has been pressed
		if request.form.get('new_project'):
			# if a project name has been entered
			if projectName != '':
				# if project name has not been used already, add it to database
				if not projectNameAlreadyExists(projectDb,projectName):
					projectDb.insert_one({"Project Name":projectName,"Description":request.form.get('description'),"HW Set 1 Resources":0,"HW Set 2 Resources":0,"Users in Project":[displayUser]})
				# print error message if the project name has already been used
				elif projectNameAlreadyExists(projectDb,projectName):
					projectMsg = "That name has already been used! Please enter a new name."
			else:
				projectMsg = "You must enter a project name."

		# if the logout button has been pressed
		if request.form.get('logout'):
			# unsave the username and return to main screen
			session.pop('username')
			return redirect(url_for('login'))
		if request.form.get('addresources'):
			project_to_manage=resourcesInfo.get("manage_project")
			projectInfo=projectDb.find_one({"Project Name": project_to_manage})
			if projectInfo is not None:	
				projectUsers=projectInfo["Users in Project"]
				if displayUser in projectUsers:
					return redirect(url_for('checkOut',project=project_to_manage)) 
				else:
					projectManageMsg="Sorry, you are not a user on this project"
			else:
				projectManageMsg="Project entered does not exist"
			#return render_template('userPortal.html',content='Hello, ' + displayUser + '!')
	return render_template('userPortal.html',content='Hello, ' + displayUser + '!',projectCheck=projectMsg, projectManageStatus= projectManageMsg)

@app.route('/checkOut/<project> ', methods=['GET','POST'])
def checkOut(project):

	msgOne= ""
	msgTwo=""
	projectInfo=projectDb.find_one({"Project Name": project})
	hwSetOne=hwDb.find_one({"ID":"HWSet_1"})
	capOne=hwSetOne["Capacity"]
	availOne=hwSetOne["Availability"]
	hwSetTwo=hwDb.find_one({"ID":"HWSet_2"})
	capTwo=hwSetTwo["Capacity"]
	availTwo=hwSetTwo["Availability"]
	if(request.method=='POST'):
		resourcesInfo = request.form
		if request.form.get("submitHW1"):
			requestedOne=int(resourcesInfo["requestedHW1"])
			result=validCheckoutInput(requestedOne, availOne)
			msgOne=error_messages[result]	
			if result==4:
				old={"ID":"HWSet_1"}
				updated={"$set": {"Availability" : availOne-requestedOne}}
				availOne=availOne-requestedOne
				hwDb.update_one(old,updated)
				project_hw1=projectInfo["HW Set 1 Resources"]
				pName={"Project Name": project}
				updatedResource={"$set": {"HW Set 1 Resources" : project_hw1 +requestedOne}}
				projectDb.update_one(pName, updatedResource)
		elif request.form.get("submitHW2"):
			requestedTwo=int(resourcesInfo["requestedHW2"])
			result=validCheckoutInput(requestedTwo,availTwo)
			msgTwo=error_messages[result]
			if result==4:
				old={"ID":"HWSet_2"}
				updated={"$set": {"Availability" : availTwo-requestedTwo}}
				availTwo=availTwo-requestedTwo
				hwDb.update_one(old,updated)
				project_hw2=projectInfo["HW Set 2 Resources"]
				pName={"Project Name": project}
				updatedResource={"$set": {"HW Set 2 Resources" : project_hw2 +requestedTwo}}
				projectDb.update_one(pName, updatedResource)
		elif request.form.get('returnToUP'):
			return redirect(url_for('userPortal'))
		elif request.form.get("checkinHW1"):
			requestedOne=int(resourcesInfo["requestedHW1"])
			project_hw1=projectInfo["HW Set 1 Resources"]
			if(requestedOne > 0 and requestedOne<=project_hw1):
				old={"ID":"HWSet_1"}
				updated={"$set": {"Availability" : availOne+requestedOne}}
				availOne=availOne+requestedOne
				hwDb.update_one(old,updated)
				pName={"Project Name": project}
				updatedResource={"$set": {"HW Set 1 Resources" : project_hw1-requestedOne}}
				projectDb.update_one(pName, updatedResource)
			else:
				msgOne="Please enter valid number of resources"
		elif request.form.get("checkinHW2"):
			requestedTwo=int(resourcesInfo["requestedHW2"])
			project_hw2=projectInfo["HW Set 2 Resources"]
			if(requestedTwo > 0 and requestedTwo<=project_hw2):
				old={"ID":"HWSet_2"}
				updated={"$set": {"Availability" : availTwo+requestedTwo}}
				availTwo=availTwo+requestedTwo
				hwDb.update_one(old,updated)
				pName={"Project Name": project}
				updatedResource={"$set": {"HW Set 2 Resources" : project_hw2-requestedTwo}}
				projectDb.update_one(pName, updatedResource)
			else:
				msgTwo="Please enter valid number of resources"
	return render_template('checkoutPage.html', available=availOne, initialCap=capOne, available2=availTwo, initialCap2=capTwo, statusOne=msgOne, statusTwo=msgTwo)

# main method that just runs the app	
if __name__ == "__main__":
	# create the hardware sets amd add them to their database
	app.run(debug=True)



