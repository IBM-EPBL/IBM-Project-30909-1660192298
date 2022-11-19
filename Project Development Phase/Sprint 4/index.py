from flask import *
from flask import Flask, render_template, request, redirect, url_for, session
from twilio.rest import Client
from werkzeug.utils import secure_filename
import ibm_db
import re
import os 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import csv
app=Flask(__name__)
app.secret_key="don't share"
myconn=ibm_db.connect('DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=ftq82843;PWD=u4VCEInPvFw43qix', '', ''
	)
@app.route("/signup")
def signup():
    return render_template("signup.html")



@app.route('/register1', methods =['GET', 'POST'])
def register1():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        query = 'SELECT * FROM admin WHERE username =?;'
        stmt=ibm_db.prepare(myconn,query)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            query = "INSERT INTO ADMIN VALUES (?,?,?)"
            stmt=ibm_db.prepare(myconn,query)
            ibm_db.bind_param(stmt,1,username)
            ibm_db.bind_param(stmt,2,email)
            ibm_db.bind_param(stmt,3,password)
            ibm_db.execute(stmt)
            msg = 'You have successfully registered !'
            return render_template('login.html', msg = msg)
	

@app.route("/login",methods=['GET','POST'])
def login():
	if request.method=="POST":
		Username=request.form['Username']
		Password=request.form['Password']
		query="select * from admin where Username=? and password=?;"
		stmt=ibm_db.prepare(myconn, query)
		ibm_db.bind_param(stmt, 1, Username)
		ibm_db.bind_param(stmt, 2, Password)
		ibm_db.execute(stmt)
		data=ibm_db.fetch_assoc(stmt)
		if data:
			session['loggedin']=True
			flash("Login Successfully")
			return  render_template('info.html')
		
		else:
			flash("Incorrect Username or Password")
	return render_template("login.html")


@app.route("/")
@app.route("/bloodbank")
def bloodbank():
		return render_template("bloodbank.html")



@app.route("/home")
def home():
	
	query="select count(*) from donor where status=1"
	stmt = ibm_db.prepare(myconn, query)
	ibm_db.execute(stmt)
	data = ibm_db.fetch_tuple(stmt)
	return render_template("index.html",data=[data])



@app.route("/register",methods=['GET','POST'])
def register():
	if request.method=="POST":
		name=request.form['name']
		email=request.form['email']
		phno=request.form['phno']
		blood_group=request.form['blood_group']
		weight=request.form['weight']
		gender=request.form['gender']
		dob=request.form['dob']
		address=request.form['address']
		adharno=request.form['adharno']
		status=1
		
		query="select * from donor where adharno=(?);"
		stmt = ibm_db.prepare(myconn, query)
		ibm_db.bind_param(stmt, 1, adharno)
		ibm_db.execute(stmt)
		data = ibm_db.fetch_assoc(stmt)
		if (data)==0:
			query = "INSERT INTO donor (NAME,EMAIL,PHNO,BLOOD_GROUP,WEIGHT,GENDER,DOB,ADDRESS,ADHARNO,STATUS) values(?,?,?,?,?,?,?,?,?,?)"
			stmt = ibm_db.prepare(myconn, query)
			ibm_db.bind_param(stmt, 1, name)
			ibm_db.bind_param(stmt, 2, email)
			ibm_db.bind_param(stmt, 3, phno)
			ibm_db.bind_param(stmt, 4, blood_group)
			ibm_db.bind_param(stmt, 5, weight)
			ibm_db.bind_param(stmt, 6, gender)
			ibm_db.bind_param(stmt, 7, dob)
			ibm_db.bind_param(stmt, 8, address)
			ibm_db.bind_param(stmt, 9, adharno)
			ibm_db.bind_param(stmt, 10, status)
			ibm_db.execute(stmt)
			msg = 'You have successfully Logged In!!'
			return redirect(url_for('viewall'))
			
		else:
			flash("Already Registered")
		return redirect(url_for('register'))
	else:
		return render_template("about.html")



@app.route("/view",methods=['GET','POST'])
def view():
	if not session.get('loggedin'):
		return  render_template("login.html")
	query="select * from donor where status=1"
	stmt = ibm_db.prepare(myconn, query)
	ibm_db.execute(stmt)
	data=[]
	tuple = ibm_db.fetch_tuple(stmt)
	while tuple!=False:
		data.append(tuple)
		tuple=ibm_db.fetch_tuple(stmt)	
	return render_template("view.html",data=data)



@app.route("/delete",methods=['GET','POST'])
def delete():
	if not session.get('loggedin'):
		return  render_template("login.html")
	if request.method=="POST":
		id=request.form['delete']
		
		query="delete from donor where sno=?"
		stmt = ibm_db.prepare(myconn, query)
		ibm_db.bind_param(stmt, 1, id)
		ibm_db.commit(stmt)
		flash("Deleted Successfully")
		return redirect(url_for('view'))



@app.route("/edit",methods=['GET','POST'])
def edit():
	if not session.get('loggedin'):
		return  render_template("login.html")
	if request.method=="POST":
		id=request.form['edit']
		
		query="select * from donor where sno=?"
		
		stmt = ibm_db.prepare(myconn, query)
		ibm_db.bind_param(stmt, 1, id)
		ibm_db.execute(stmt)
		data = ibm_db.fetch_tuple(stmt)
		return render_template("edit.html",data=data)



@app.route("/update",methods=['GET','POST'])
def update():
	if not session.get('loggedin'):
		return  render_template("login.html")
	if request.method=="POST":
		id=request.form['id']
		name=request.form['name']
		email=request.form['email']
		phno=request.form['phno']
		blood_group=request.form['blood_group']
		weight=request.form['weight']
		gender=request.form['gender']
		dob=request.form['dob']
		address=request.form['address']
		adharno=request.form['adharno']

	
		query = "INSERT INTO USER1 values(?,?,?,?,?,?,?,?,?,?)"
		stmt = ibm_db.prepare(myconn, query)
		ibm_db.bind_param(stmt, 1, id)
		ibm_db.bind_param(stmt, 2, name)
		ibm_db.bind_param(stmt, 3, email)
		ibm_db.bind_param(stmt, 4, phno)
		ibm_db.bind_param(stmt, 5, blood_group)
		ibm_db.bind_param(stmt, 6, weight)
		ibm_db.bind_param(stmt, 7, gender)
		ibm_db.bind_param(stmt, 8, dob)
		ibm_db.bind_param(stmt, 9, address)
		ibm_db.bind_param(stmt, 10, adharno)
		ibm_db.commit(stmt)
		return redirect(url_for('view'))
	
	

@app.route("/view2",methods=['GET','POST'])
def view2():
	
	query="select distinct blood_group from donor where status=1"
	stmt = ibm_db.prepare(myconn, query)
	ibm_db.execute(stmt)
	data=[]
	tuple = ibm_db.fetch_tuple(stmt)
	while tuple!=False:
		data.append(tuple)
		tuple=ibm_db.fetch_tuple(stmt)
	return render_template("select.html",data=data)


@app.route("/viewselected",methods=['GET','POST'])
def viewselected():
	blood_group=request.form['blood_group']
	query="select * from donor where blood_group= ? and status=1"
	stmt = ibm_db.prepare(myconn, query)
	ibm_db.bind_param(stmt, 1, blood_group)
	ibm_db.execute(stmt)
	data=[]
	tuple = ibm_db.fetch_tuple(stmt)
	while tuple!=False:
		data.append(tuple)
		tuple=ibm_db.fetch_tuple(stmt)
	return render_template("view2.html",data=data)
	

@app.route("/viewall",methods=['GET','POST'])
def viewall():
	
	query="select * from donor where status=1"
	stmt = ibm_db.prepare(myconn, query)
	ibm_db.execute(stmt)
	data=[]
	tuple = ibm_db.fetch_tuple(stmt)
	while tuple!=False:
		data.append(tuple)
		tuple=ibm_db.fetch_tuple(stmt)
	return render_template("view2.html",data=data)


@app.route("/")
@app.route("/send",methods=['GET','POST'])
def send():
	if request.method=="POST":
		id=request.form['send']

		query="select email from donor where sno=?"
		
		stmt = ibm_db.prepare(myconn, query)
		ibm_db.bind_param(stmt, 1, id)
		ibm_db.execute(stmt)
		data = ibm_db.fetch_assoc(stmt)
		print(data) 
		message = Mail(from_email='empire44440@gmail.com',to_emails=data['EMAIL'],subject='Hi Donor!!!',html_content='<strong>We searching for a plasma donor and last we found your match is safe with our patient.Kindly contact us at your convenience</strong>')
		try:
			sg = SendGridAPIClient('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')
			response = sg.send(message)
			print(response.status_code)
			print(response.body)
			print(response.headers)
		except Exception as e:
			print(e)
	return redirect('/viewall')


@app.route("/logout")
def logout():
	session['loggedin']=False
	return render_template("index.html")



@app.route("/hold",methods=['GET','POST'])
def hold():
	if not session.get('loggedin'):
		return  render_template("login.html")
	if request.method=="POST":
		id=request.form['hold']
		query="update donor set  status=0 where sno=?"
		stmt = ibm_db.prepare(myconn, query)
		ibm_db.bind_param(stmt, 1, id)
		ibm_db.execute(stmt)
		
		return redirect(url_for('view'))



@app.route("/activate",methods=['GET','POST'])
def activate():
	if not session.get('loggedin'):
		return  render_template("login.html")
	if request.method=="POST":
		id=request.form['hold']
		
		query="update donor set  status=1 where sno=?"
		stmt = ibm_db.prepare(myconn, query)
		ibm_db.bind_param(stmt, 1, id)
		ibm_db.execute3(stmt)
		
		return redirect(url_for('inactive'))


@app.route("/inactive",methods=['GET','POST'])
def inactive():
	if not session.get('loggedin'):
		return  render_template("login.html")

	query="select * from donor where status=0"
	stmt = ibm_db.prepare(myconn, query)
	ibm_db.execute(stmt)
	data = ibm_db.fetch_tuple(stmt)
	print(data)
	return render_template('inactive.html',data=[data])



if __name__=="__main__":
	app.run(debug=True)
