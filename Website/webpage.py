from flask import Flask, render_template,url_for, request, redirect, session
from flask_pymongo import PyMongo
app = Flask(__name__)

app.config["MONGO_URI"] = 'mongodb+srv://mainUser:TahoeMontecito!@461l-team8.lchei.mongodb.net/myDb?retryWrites=true&w=majority'
mongo = PyMongo(app)
user = mongo.db.users

# just have a / means that's the home page
@app.route('/',methods=['GET','POST'])
def login():
	invalidName = False
	invalidPassword = False
	# if we have submitted a form
	if(request.method=='POST'):
		# loginInfo is a dictionary that contains as keys the names of the input fields in the form group and the actual user input as values
		loginInfo = request.form
		# check if the username or password fields are empty
		if not loginInfo.get('username'):
			invalidName = True
		if not loginInfo.get('password'):
			invalidPassword = True
		#print(loginInfo)
		if(invalidName and not invalidPassword):
			return render_template('userLoginPage.html',content='Empty Username!')
		elif(not invalidName and invalidPassword):
			return render_template('userLoginPage.html',content='Empty Password!')
		elif(invalidName and invalidPassword):
			return render_template('userLoginPage.html',content='Empty Username and Password!')
		else:
			# if a username and password have been submitted, add them to the database
			user.insert_one({"username":loginInfo.get('username'), "password":loginInfo.get('password')})
			return render_template('projectPage.html')
			return redirect('projectPage.html')
		return redirect(request.url)
	return render_template('userLoginPage.html')

# below displays the HTML for the user portal page
@app.route('/projectPage',methods=['GET','POST'])
def project():
	return render_template('projectPage.html')

# main method that just runs the app	
if __name__ == "__main__":
	app.run(debug=True)

