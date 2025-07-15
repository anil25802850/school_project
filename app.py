from flask import Flask,flash,redirect,render_template,url_for,request,Response,session,jsonify
import mysql.connector
import requests
import bcrypt
import mysql
from flask_session import Session
from cmail import send_mail
from otp import genotp
from numbergenerator import full_id

app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
app.secret_key='schoolprj'
Session(app)

mydb=mysql.connector.connect(user='root',host='localhost',password='Anilk',database='school')

@app.route('/')
def home():
    return render_template('index.html')


# Route to generate OTP for teacher signup
@app.route('/otpgeneration/<mailid>', methods=['GET'])
def otpgeneration(mailid):
    cursor = mydb.cursor(buffered=True)
    cursor.execute('select count(email_id) from teachers where email_id=%s', [mailid])
    count = cursor.fetchone()[0]
    if count == 0:
        otp = genotp()
        session['otp'] = otp
        print('otp=====================',otp)
        send_mail(to=mailid, subject='OTP for School Management System', body=f'Your OTP is {otp}')
        session['status'] = 'success'
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'mailid already exists'})
    
    
    
# Route to handle teacher signup
@app.route('/teachersignup', methods=['GET', 'POST'])
def teachersignup():
    cursor = mydb.cursor(buffered=True)
    cursor.execute("SELECT school_name,id FROM school")
    school_names = cursor.fetchall() #[('NARAYANA',1),()]
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']  # Capture teacher name
        otp_input = request.form['otp']
        print(session['otp'],otp_input)
        school_id = request.form['school']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        id = full_id(school_id=school_id,person='teacher')  # Ensure this is a function returning string
        print(id)
        if otp_input==session.get('otp'):
            cursor.execute(
            'INSERT INTO teachers(id, name, email_id, school_id, password) VALUES (%s, %s, %s, %s, %s)',
            (id, name, email, school_id, hashed_password)
        )
            mydb.commit()
            flash('Teacher registered successfully', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid OTP', 'danger')
            return redirect(url_for('teachersignup'))
    return render_template('signup.html', school_names=school_names)

@app.route('/teacherlogin',methods=['GET','POST'])
def teacherlogin():
    cursor=mydb.cursor()
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        cursor.execute('select count(email_id) from teachers where email_id=%s',[email])
        count=cursor.fetchone()[0]
        if count==0:
            flash('user not exists')
            return redirect(url_for('teachersignup'))
        else:
            cursor.execute('select password from teachers where email_id=%s',[email])
            db_password=cursor.fetchone()[0]
            if bcrypt.checkpw(password.encode(),db_password):
                session['email'] = email
                flash('Login successful', 'success')    
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Password')
                return redirect(url_for('teacherlogin'))
    return render_template('teacherlogin.html')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    cursor=mydb.cursor()
    cursor.execute('select school_id from teachers where email_id=%s',[session['email']])
    session['school_id']=cursor.fetchone()[0]
    cursor.execute('select class_number from classes where school_id=%s',[session['school_id']])
    classes = [row[0] for row in cursor.fetchall()]
    return render_template('dashboard.html',classes=classes)

@app.route('/addstudent',methods=['GET','POST'])
def addstudent():
    if request.method=='POST':
        name=request.form['name']
        parent=request.form['parent']
        class_id=request.form['class']
        phone=request.form['phone']
        email=request.form['email']
        address=request.form['address']
        cursor=mydb.cursor()
        id=full_id(school_id=session['school_id'],person='student')
        cursor.execute('insert into student values(%s,%s,%s,%s,%s,%s,%s,%s)',[id,name,parent,phone,email,address,int(session['school_id']),class_id])
        mydb.commit()
        return redirect(url_for('dashboard'))

@app.route('/fetchstudents',methods=['GET','POST'])
def fetchstudents(): 
   
@app.route('/modifystudent',methods=['GET','POST'])
def modifystudent():
    
    
@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        school_name = request.form['school']
        address=request.form['address']
        city=request.form['city']
        start=int(request.form['start'])
        end=int(request.form['end'])
        cursor = mydb.cursor()
        cursor.execute('INSERT INTO school (school_name,address,city) VALUES (%s,%s,%s)', (school_name,address,city))
        mydb.commit()
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select id from school where school_name=%s', [school_name])
        id=cursor.fetchone()[0]
        for i in range(start,end+1):
            class_name = f'Class-{i}'
            cursor = mydb.cursor()
            cursor.execute('INSERT INTO classes (school_id, class_number) VALUES (%s, %s)', (id, class_name))
            mydb.commit()
        flash('School added successfully', 'success')
        return redirect(url_for('admin'))
    return render_template('admin.html')
    
app.run(use_reloader=True, debug=True)