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

mongo4 = PyMongo(app,uri='mongodb+srv://mainUser:TahoeMontecito!@461l-team8.lchei.mongodb.net/datasets?retryWrites=true&w=majority')
datasetsDB = mongo.db.datasets


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
	#print(userFound["password"])
	if(userFound["password"] == password):
		return True
	return False

# returns true if a project name already exists
def projectNameAlreadyExists(database,name):
	if database.find_one({"Project Name":name}) == None:
		return False
	else:
		return True


# just having a / means that's the home page
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
	projectJoinMsg=""
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
		
		# if the  Go to Project Portal button has been pressed
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

		# if the Join Preexisting Project Button has been pressed
		if request.form.get('joinproject'):
			project_to_join=resourcesInfo.get("join_project")
			projectInfo=projectDb.find_one({"Project Name": project_to_join})
			if projectInfo is not None:
				projectUsers=projectInfo["Users in Project"]
				#if user is found in project database, then they should not be added again
				if displayUser in projectUsers:
					projectJoinMsg="You are already a user on this project"
				#if user is not already in project, they may join the project
				else:
					#old = {"Project Name": projectInfo["Project Name"], "Description":projectInfo["Description"], "HW Set 1 Resources":projectInfo["HW Set 1 Resources"], "HW Set 2 Resources":projectInfo["HW Set 1 Resources"]}
					#print(projectUsers)
					projectUsers.append(displayUser)
					#print(projectUsers)
					# updated = {'$set': {"Users in Project": projectUsers}}
					# projectDb.update_one(old, updated)
					projectDb.update({"Project Name": projectInfo["Project Name"]},{'$set':{"Users in Project":projectUsers}})
					projectJoinMsg = "Successfully joined project!"
			else:
				projectJoinMsg="Project entered does not exist" 

		# if the logout button has been pressed
		if request.form.get('logout'):
			# unsave the username and return to main screen
			session.pop('username')
			return redirect(url_for('login'))

		# if the Delete Account button has been pressed
		if request.form.get('delete'):
			userDb.delete_one({"username":displayUser})
			session.pop('username')
			return redirect(url_for('login'))

		if request.form.get('changePswrd'):
			return redirect(url_for('changePassword'))

		#if the Change Password button has been pressed
				
	return render_template('userPortal.html',content='Hello, ' + displayUser + '!',projectCheck=projectMsg, projectManageStatus= projectManageMsg, joinStatus=projectJoinMsg)

@app.route('/changePass', methods=['GET','POST'])
def changePassword():
	username = session['username']
	user = userDb.find_one({'username':username})
	password = user['password']
	msg = ""
	if(request.method == 'POST'):
		inputs = request.form
		if inputs.get('new'):
			if not inputs.get('old password') or not inputs.get('new password') or not inputs.get('confirm password'):
				msg = "Empty field found"
			elif inputs.get('old password') != password and inputs.get('new password') == inputs.get('confirm password'):
				msg = "Previous password is not correct!"
			elif inputs.get('new password') != inputs.get('confirm password') and inputs.get('old password') == password:
				msg = "New passwords do not match!"
			elif inputs.get('old password') != password and inputs.get('new password') != inputs.get('confirm password'):
				msg = "Previous password is not correct and the new passwords do not match!"
			elif inputs.get('old password') == password and inputs.get('new password') == inputs.get('confirm password'):
				userDb.update_one({'username':username},{'$set':{'password':inputs.get('new password')}})
		elif inputs.get('back'):
			return redirect(url_for('userPortal'))
	return render_template('changePass.html',content=msg)

@app.route('/checkOut/<project> ', methods=['GET','POST'])
def checkOut(project):
	hwSetList=set()
	print(hwDb)
	x=hwDb.find({},{'_id' : 0,'Capacity':0, 'Availability':0})
	for data in x:
		if data["ID"] not in hwSetList:
			hwSetList.add(data["ID"])
	hwSetList = list(hwSetList)
	msgOne= ""
	msgTwo=""
	user = ""
	projectLeaveMsg = ""
	modifyingProject= "Modifying project: " + project
	projectInfo=projectDb.find_one({"Project Name": project})
	hwSetOne=hwDb.find_one({"ID":"HWSet_1"})
	capOne=hwSetOne["Capacity"]
	availOne=hwSetOne["Availability"]
	hwSetTwo=hwDb.find_one({"ID":"HWSet_2"})
	capTwo=hwSetTwo["Capacity"]
	availTwo=hwSetTwo["Availability"]
	user = session['username']   
	session['project'] = project                      
	if(request.method=='POST'):
		resourcesInfo = request.form
		if request.form.get("submitHW1"):
			if not resourcesInfo["requestedHW1"]:
				msgOne="Please enter a nonempty value"
			else:
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
			if not resourcesInfo["requestedHW2"]:
				msgTwo="Please enter a nonempty value"
			else:
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
			session.pop('project')
			return redirect(url_for('userPortal'))
		elif request.form.get('leaveproject'):
			projectUsers=projectInfo["Users in Project"]
			projectUsers.remove(user)
			projectDb.update({"Project Name": projectInfo["Project Name"]},{'$set':{"Users in Project":projectUsers}})
			session.pop('project')
			return redirect(url_for('userPortal'))
                                
		elif request.form.get("checkinHW1"):
			if resourcesInfo["requestedHW1"]:
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
			else:
				msgOne="Please enter a nonempty value"
		elif request.form.get("checkinHW2"):
			if resourcesInfo["requestedHW2"]:
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
			else:
				msgTwo="Please enter a nonempty value"
	return render_template('checkoutPage.html', displayProject=modifyingProject,available=availOne, initialCap=capOne, available2=availTwo, initialCap2=capTwo, statusOne=msgOne, statusTwo=msgTwo, listHWs=hwSetList)


#This is for the main datasets page
@app.route('/datasets', methods = ["POST", "GET"])
def home():
	if request.method == "POST":
		user = request.form["username"]
		return redirect(url_for("fnd", he = user))
	else:
		return render_template("datasetpage.html")

#This page is for adding new datasets
@app.route('/datasets/index')
def index():
	return '''
		<form method = "POST" action ="/create" enctype = "multipart/form-data">
			<input type ="text" name ="username">
			<input type ="text" name = "description">
			<input type ="file" name ="data">
			<input type ="submit">
		</form>
	'''

#This is used by '/index' to create new datasets
@app.route('/datasets/create', methods=['POST'])
def create():
	if 'data' in request.files:
		data = request.files['data']
		mongo4.save_file(data.filename, data)
		mongo4.db.sets.insert({'username' : request.form.get('username'), 'description' : request.form.get('description'), 'data_name' : data.filename})
		
	return 'done'

#done <iframe src = "{url_for('file', filename = user['description'])}" width = "100%" height = "300">

#This is used by 'fnd' to find and download the correct datasets
@app.route('/datasets/file/<filename>')
def file(filename):
	return mongo4.send_file(filename)


#This page finds and downloads the correct datasets
@app.route('/datasets/fnd/<he>', methods = ["POST", "GET"])
def fnd(he):
	#index()
	print(he)
	#if(he == "data2.zip"):
	#	se = mongo.db.fs.files.find({'filename' : "data2.zip"})

	se = mongo4.db.fs.files.find({'filename' : he})
	a = ["a", "b"]
	for st in se:
		a.append(st)
	bill = str(a)
	z = bill.split("filename': '", 1)
	bill = z[1]
	y = z[1].split("'", 1)
	bill = y[0]
	user = mongo4.db.sets.find_one_or_404({'data_name' : y[0]})
	return f'''
		<h1>{bill}</h1>
		<h1>{he}</h1>
		<iframe src ="{url_for('file', filename =user['data_name'])}" width = "0%"  height = "0">
		'''







# main method that just runs the app	
if __name__ == "__main__":
	# create the hardware sets amd add them to their database
	app.run(debug=True)



