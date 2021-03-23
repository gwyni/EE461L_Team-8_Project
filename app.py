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

			# if the the inputted username has not already been used, add username and password to the database
			elif not userNameAlreadyExists(userDb,username):
				userDb.insert_one({"username":loginInfo.get('username'), "password":loginInfo.get('password')})
				session['username'] = username
				#print(session['username'])
				#return render_template('userPortal.html')
				return redirect(url_for('userPortal'))
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
	msgOne= ""
	msgTwo=""
	hwSetOne=hwDb.find_one({"ID":"HWSet_1"})
	capOne=hwSetOne["Capacity"]
	availOne=hwSetOne["Availability"]
	hwSetTwo=hwDb.find_one({"ID":"HWSet_2"})
	capTwo=hwSetTwo["Capacity"]
	availTwo=hwSetOne["Availability"]
	displayUser = ""
	if 'username' in session:
			displayUser = session['username']
	if(request.method=='POST'):
		projectInfo = request.form
		projectName = projectInfo.get('Project Name')
		if "requestedHW1" in projectInfo.keys():
			requestedOne=int(projectInfo["requestedHW1"])
			result=validCheckoutInput(requestedOne, availOne)
			msgOne=error_messages[result]		
		elif "requestedHW2" in projectInfo.keys():
			requestedTwo=int(projectInfo["requestedHW2"])
			result=validCheckoutInput(requestedTwo,availTwo)
			msgTwo=error_messages[result]
			
		
			
		#return render_template('userPortal.html',content='Hello, ' + displayUser + '!')
	return render_template('userPortal.html',content='Hello, ' + displayUser + '!', available=availOne, initialCap=capOne, available2=availTwo, initialCap2=capTwo, statusOne=msgOne, statusTwo=msgTwo)

@app.route('/checkOut/', methods=['GET','POST'])
def checkOut():
	msgOne= ""
	msgTwo=""
	#print("Printing Database")
	#printDatabase(hwDb)
	hwSetOne=hwDb.find_one({"ID":"HWSet_1"})
	capOne=hwSetOne["Capacity"]
	availOne=hwSetOne["Availability"]
	hwSetTwo=hwDb.find_one({"ID":"HWSet_2"})
	capTwo=hwSetTwo["Capacity"]
	availTwo=hwSetOne["Availability"]
	if(request.method=='POST'):
		checkOutInfo=request.form
		if "requestedHW1" in checkOutInfo.keys():
			requestedOne=int(checkOutInfo["requestedHW1"])
			result=validCheckoutInput(requestedOne, availOne)
			msgOne=error_messages[result]
		elif "requestedHW2" in checkOutInfo.keys():
			requestedTwo=int(checkOutInfo["requestedHW2"])
			result=validCheckoutInput(requestedTwo,availTwo)
			msgTwo=error_messages[result]
		
		#print(checkOutInfo)
	return render_template('checkOutPage.html', available=capOne, initialCap=availOne, available2=capTwo, initialCap2=availTwo, statusOne=msgOne, statusTwo=msgTwo)
# main method that just runs the app	
if __name__ == "__main__":
	# create the hardware sets amd add them to their database
	app.run(debug=True)



