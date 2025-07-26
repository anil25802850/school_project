from flask import Flask,flash,redirect,render_template,url_for,request,Response,session,jsonify
import mysql.connector
import requests
import bcrypt
import mysql
from flask_session import Session
from cmail import send_mail
from otp import genotp


app=Flask(__name__)
app.config['SESSION_TYPE']='filesystem'
app.secret_key='schoolprj'
Session(app)

mydb=mysql.connector.connect(user='root',host='localhost',password='Anilk',db='school')

@app.route('/')
def home():
    return render_template('dashboard.html')


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
  #=============================================================================  
    
    
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
    return render_template('teachersignup.html', school_names=school_names)
#=============================================================================

# Route to handle teacher login
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
                session['teacher'] = email
                flash('Login successful', 'success')    
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Password')
                return redirect(url_for('teacherlogin'))
    return render_template('teacherlogin.html')
#=========================================================================

# Route to handle teacher logout
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    cursor=mydb.cursor()
    cursor.execute('select school_id from teachers where email_id=%s',[session['teacher']])
    session['school_id']=cursor.fetchone()[0]
    cursor.execute('select class_number from classes where school_id=%s',[session['school_id']])
    classes = [row[0] for row in cursor.fetchall()]
    session['classes'] = classes
    print('classes=====================',session['classes'])
    return render_template('dashboard.html',classes=session['classes'])
#=========================================================================

# Route to handle student signup
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
        print(id)
        cursor.execute('insert into student values(%s,%s,%s,%s,%s,%s,%s,%s)',[id,name,parent,phone,email,address,int(session['school_id']),class_id])
        mydb.commit()
        flash(f'Student {name} added successfully')
        return redirect(url_for('addstudent'))
    return render_template('addstudent.html',classes=session['classes'])
#=========================================================================    
    
        
    
    
# Route to handle admin page for adding schools and classes
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
#-----------------------------------------------------------------------------


@app.route('/fetchstudents', methods=['GET','POST'])
def fetchstudents():  
    cursor = mydb.cursor(buffered=True)
    if request.method == 'POST':
        class_id = request.form['class']
        session['class_id'] = class_id
        cursor.execute('SELECT * FROM student WHERE class_number = %s AND school_id = %s', (class_id, session['school_id']))
        session['students'] = cursor.fetchall()
        if session['students']==[]:
            session['nostudents'] = 'No students found in this class'
        print(session['students'],'===============================================')
        return redirect(url_for('fetchstudents'))
    return render_template('fetchstudents.html')
#-------------------------------------------------------

@app.route('/studentlogin', methods=['GET', 'POST'])
def studentlogin():
    cursor = mydb.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute('SELECT count(email_id) FROM student WHERE email_id=%s', [email])
        count = cursor.fetchone()[0]
        if count == 0:
            flash('User does not exist')
            return redirect(url_for('studentlogin'))
        else:
            cursor.execute('SELECT password FROM student WHERE email_id=%s', [email])
            db_password = cursor.fetchone()[0]
            if bcrypt.checkpw(password.encode(), db_password):
                session['student'] = email
                flash('Login successful', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Password')
                return redirect(url_for('studentlogin'))
    return render_template('studentlogin.html') #-------------------------------------------------------

@app.route('/updatestudent/<student_id>', methods=['GET', 'POST'])
def updatestudent(student_id):
    cursor = mydb.cursor()
    if request.method == 'POST':
        name = request.form['name']
        parent = request.form['parent']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        class_id = request.form['class']
        cursor.execute('UPDATE student SET name=%s, parent_name=%s, phone=%s, mail=%s, address=%s, class_number=%s WHERE id=%s',
                       (name, parent, phone, email, address, class_id, student_id))
        mydb.commit()
        flash('Student updated successfully', 'success')
        return redirect(url_for('fetchstudents'))
    cursor.execute('SELECT * FROM student WHERE id=%s', [student_id])
    student = cursor.fetchone()
    return render_template('updatestudent.html', student=student, classes=session['classes'])

@app.route('/deletestudent/<student_id>', methods=['GET'])
def deletestudent(student_id):
    cursor = mydb.cursor()
    cursor.execute('DELETE FROM student WHERE id=%s', [student_id])
    mydb.commit()
    flash('Student deleted successfully', 'success')
    return redirect(url_for('fetchstudents'))

@app.route('/logout', methods=['GET'])
def logout():
    if session.get('teacher'):
        session.clear()
        return redirect(url_for('home'))
    if session.get('student'):
        session.clear()
        return redirect(url_for('home'))
    #------------------------------------------------------------------------------------------
    
    
@app.route('/faculty', methods=['GET','POST'])  
def faculty():
    print(request.form)
    mydb=mysql.connector.connect(user='root',host='localhost',password='Anilk',db='school')
    cursor=mydb.cursor()
    cursor.execute('select school_id from teachers where email_id=%s',[session['teacher']])
    session['school_id']=cursor.fetchone()[0]
    cursor.execute('select name,email_id,id from teachers where school_id=%s',[session['school_id']])
    teachers = cursor.fetchall()
    cursor.execute('select distinct subject_name from subjects where school_id=%s',[session['school_id']])
    subjects = cursor.fetchall()
    subjects = [subject[0] for subject in subjects]  # Extract subject names from tuples
    session['subjects'] = subjects
    session['teachers'] = teachers
    cursor.execute('select distinct subject_name,name from subjects join teachers on subjects.teacher_id=teachers.id; where school_id=%s',[session['school_id']])
    subteachers=cursor.fetchall()
    session['subteachers'] = subteachers
    if request.method == 'POST':
        teacher= request.form['teacher']
        subject = request.form['subject']
        try:
            mydb=mysql.connector.connect(user='root',host='localhost',password='Anilk',db='school')
            cursor = mydb.cursor()
            cursor.execute('update subjects set teacher_id=%s where subject_name=%s',[teacher,subject])
            mydb.commit()
        except mysql.connector.Error as err:
            print(f'Error: {err}', 'danger')
            flash('Error assigning subject to teacher')
            return redirect(url_for('faculty'))
        else:
            flash('Subject assigned to teacher successfully', 'success')
            return redirect(url_for('faculty'))
    return render_template('faculty.html')

@app.route('/subjects',methods=['GET','POST'])
def subjects():
    cursor=mydb.cursor()
    cursor.execute('select subject_name,class_number,id from subjects where school_id=%s',[session['school_id']])
    session['subjects']=cursor.fetchall()
    if session.get('subjects'):
        print(session['subjects'])
    if request.method == 'POST':
        try:
            class_id = request.form['class']
            subject=request.form['subject']
            cursor.execute('select id from teachers where email_id=%s',[session['teacher']])
            teacher_id = cursor.fetchone()[0]
            session['teacher_id'] = teacher_id
            cursor.execute('insert into subjects(school_id,subject_name,class_number,teacher_id) values(%s,%s,%s,%s)',[session['school_id'],subject,class_id,teacher_id])
            mydb.commit()
            
        except mysql.connector.Error as err:
            print(f'Error: {err}', 'danger')
            flash('Subject already exists or other error')
            return redirect(url_for('subjects'))
        else:
            cursor.execute('select subject_name,class_number,id from subjects where school_id=%s',[session['school_id']])
            subjects = cursor.fetchall()
            print('==========================\n', subjects, '\n==========================')
            session['subjects'] = subjects
            flash('Subject added successfully', 'success')
            return redirect(url_for('subjects'))
    return render_template('subjects.html')

@app.route('/deletesubject/<subject_id>', methods=['GET'])
def deletesubject(subject_id):
    cursor = mydb.cursor()
    cursor.execute('DELETE FROM subjects WHERE id=%s', [subject_id])
    mydb.commit()
    cursor.execute('select subject_name,class_number,id from subjects where school_id=%s',[session['school_id']])
    subjects = cursor.fetchall()
    print('==========================\n', subjects, '\n==========================')
    session['subjects'] = subjects
    flash('Subject deleted successfully', 'success')
    cursor
    return redirect(url_for('subjects'))

@app.route('/marks', methods=['GET', 'POST'])
def marks():
    # displaymarks()
    marks={}
    if request.method=='POST':
        class_id=request.form['class']
        session['class_id']=class_id
        cursor=mydb.cursor()
        cursor.execute('select id,name from student where school_id=%s and class_number=%s',[session['school_id'],class_id])
        studentnames=cursor.fetchall()
        session['studentnames']=studentnames
        for item in session['studentnames']:
            if total_marks(item[0])==None:
                tmarks=0
            else:
                tmarks=total_marks(item[0])
            marks[item[0]]=tmarks
        # marks=marks
        marks=rankcalculator(marks)
        print(marks)
        print(session['studentnames'])
    return render_template('studentnames.html',marks=marks)

@app.route('/studentmarks/<id>',methods=['GET','POST'])
def studentmarks(id):
    cursor=mydb.cursor()
    cursor.execute('select name,class_number from student where id=%s',[id])
    details=cursor.fetchone()
    cursor.execute('select * from subjects where class_number=%s',[session['class_id']])
    class_subjects=cursor.fetchall()
    print('class subjects\n',class_subjects)
    session['class_subjects']=class_subjects
    cursor.execute('select sum(marks) from marks where student_id=%s',[id])
    totalmarks=cursor.fetchone()[0]
    if request.method=='POST':
        datamarks=request.get_json()
        for s_id,marks in datamarks.items():
            cursor= mydb.cursor()
            grades=grade(int(marks))
            statuss=status(int(marks))
            print('Details=======================\n',[session['school_id'],id,s_id,session['class_subjects'][0][3],marks,grades,statuss])
            cursor.execute('insert into marks values(%s,%s,%s,%s,%s,%s,%s)',[session['school_id'],id,s_id,session['class_id'],marks,grades,statuss])
            mydb.commit()
            print(f'Subject with Id {s_id} added successfully')
        print('marks', marks)
        flash(f'Marks added successfully for {details[0]}')
        return jsonify({'redirect':url_for('marks')})
    return render_template('studentmarks.html',details=details,totalmarks=totalmarks)

#Update Route
@app.route('/updatemarks/<id>',methods=['GET','POST'])
def updatemarks(id):
    cursor=mydb.cursor()
    cursor.execute('select name,class_number from student where id=%s',[id])
    details=cursor.fetchone()
    cursor.execute('select * from subjects where class_number=%s',[session['class_id']])
    class_subjects=cursor.fetchall()
    print('class subjects\n',class_subjects)
    session['class_subjects']=class_subjects
    cursor.execute('select sum(marks) from marks where student_id=%s',[id])
    totalmarks=cursor.fetchone()[0]
    if request.method=='POST':
        datamarks=request.get_json()
        for s_id,marks in datamarks.items():
            cursor= mydb.cursor()
            grades=grade(int(marks))
            statuss=status(int(marks))
            print('Details=======================\n',[session['school_id'],id,s_id,session['class_subjects'][0][3],marks,grades,statuss])
            cursor.execute('update marks set marks=%s,grade=%s,status=%s where student_id=%s and subject_id=%s',[marks,grades,statuss,id,s_id])
            mydb.commit()
            print(f'Subject with Id {s_id} updated successfully')
        print('marks', marks)
        flash(f'Marks updated successfully for {details[0]}')
        return jsonify({'redirect':url_for('marks')})
    return render_template('studentmarks.html',details=details,totalmarks=totalmarks)


@app.route('/sessiondetails', methods=['GET', 'POST'])
def sessiondetails():
    sessiondetails=session
    return render_template('sessiondetails.html',sessiondetails=sessiondetails)

def total_marks(student_id):
    cursor=mydb.cursor()
    cursor.execute('select sum(marks) from marks where student_id=%s',[student_id])
    total_marks_db = cursor.fetchone()[0]
    print('========================',total_marks_db)
    session['total_marks'] = total_marks_db
    return total_marks_db

def full_id(school_id,person):
    cursor=mydb.cursor()
    cursor.execute('SELECT SCHOOL_NAME FROM SCHOOL WHERE ID=%s',[school_id])
    school_name =cursor.fetchone()[0]
    first_3letters = school_name[0:3].upper()
    s_id=int(school_id) #1 017  
    if s_id < 10:
        school_id = '00' + str(s_id)
    elif s_id < 100:
        school_id = '0' + str(s_id)
    else:
        school_id = str(s_id)
    person = person
    print(person)
    t_id = 'T' if person == 'teacher' else 'S'
    till_now = first_3letters + school_id + t_id + '%'
    print(till_now)
    if person == 'teacher':
        cursor.execute('select max(id) from teachers where id like %s', [till_now])
        maximum = cursor.fetchone()[0]
    elif person=='student':
        cursor.execute('select max(id) from student where id like %s', [till_now])
        maximum = cursor.fetchone()[0]
    print('maximum', maximum)
    if maximum is None:
        maximum = '000'
    last = int(maximum[-3::]) + 1
    if last < 10:
        last = '00' + str(last)
    elif last < 100:
        last = '0' + str(last)
    else:
        last = str(last)
    print('max', maximum)
    print('last', last)
    full_id = first_3letters + str(school_id) + t_id + last
    print('full_id', full_id)
    return str(full_id)

def displaymarks():
    session['marks']=None
    try:
        if session['studentnames']:
            for item in session['studentnames']:
                print('Item:     ',item)
                total=total_marks(item[0])
                print(item[0],total)
                if item[0]!=None:
                    session['marks'][item[0]]=total
    except Exception as e:
        print(f'{e}')
        flash('Something went wrong')
        return redirect(url_for('marks'))
    else:
        return session['marks']
    # return session['marks']

def rankcalculator(marks):
    a=list(sorted(marks,key=lambda x:marks[x],reverse=True))
    print(a)
    ranks=[]
    for index,item in enumerate(a):
        ranks+=[[item,index+1]]
    print(ranks)
    for key,values in marks.items():
        for rank in ranks:
            if key==rank[0]:
                marks[key]=[values,rank[1]]
    return marks

def grade(marks):
    if marks >= 90:
        return 'A+'
    elif marks >= 80:
        return 'A'
    elif marks >= 70:
        return 'B+'
    elif marks >= 60:
        return 'B'
    elif marks >= 35:
        return 'C'
    else:
        return 'F'
    
def status(marks):
    if marks >= 35:
        return 'Pass'
    else:
        return 'Fail'
app.run(debug=True,use_reloader=True)
