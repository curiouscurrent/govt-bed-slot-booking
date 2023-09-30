from flask import Flask, json,redirect,render_template,request,flash,url_for,session
from sqlalchemy import create_engine,text,engine
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_required,login_user,logout_user,login_manager,LoginManager,current_user,user_loaded_from_request
from werkzeug.security import generate_password_hash,check_password_hash
from flask_mail import Mail
import json

# mydatabase connection
local_server=True
app=Flask(__name__)
app.secret_key="anusha"

# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'


# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databsename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/bedsearch'
db=SQLAlchemy(app)

with open('config.json','r') as c:
    params=json.load(c)["params"]

app.config.update(
     MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password'])
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id))


class test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))

class User(UserMixin,db.Model):
   id=db.Column(db.Integer,primary_key=True) 
   upi_id=db.Column(db.String(20),unique=True)
   email=db.Column(db.String(100))
   dob=db.Column(db.String(1000))

class Hospitaluser(UserMixin,db.Model):
   id=db.Column(db.Integer,primary_key=True) 
   hcode=db.Column(db.String(20),unique=True)
   email=db.Column(db.String(100))
   password=db.Column(db.String(1000))

class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(200),unique=True)
    hname=db.Column(db.String(200))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)

class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upi_id=db.Column(db.String(20),unique=True)
    bedtype=db.Column(db.String(100))
    hcode=db.Column(db.String(20))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(100))
    pphone=db.Column(db.String(100))
    paddress=db.Column(db.String(100))

class Trig(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)
    querys=db.Column(db.String(50))
    date=db.Column(db.String(50))

@app.route("/")
def home():
   
    return render_template("index.html")

# testing wheather db is connected or not  
@app.route("/Test")
def Test():
    try:
        a=test.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'MY DATABASE IS NOT CONNECTED {e}'
    
@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        upi_id =request.form.get('upi_id')
        email = request.form.get('email')
        dob = request.form.get('dob')
        print(upi_id,email,dob)
        encpassword=generate_password_hash(dob)
        user=User.query.filter_by(upi_id=upi_id).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or UPI ID is already taken","warning")
            return render_template("usersignup.html")
        # new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{encpassword}') ")
        new_user=User(upi_id=upi_id,email=email,dob=encpassword)
        db.session.add(new_user)
        db.session.commit()

        
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")
        
                
        

    
    
    return render_template("usersignup.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        upi_id =request.form.get('upi_id')
        dob = request.form.get('dob')
        user = User.query.filter_by(upi_id=upi_id).first()

        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("LOGIN SUCCESS","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")
      

    return render_template("userlogin.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
 
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username==params['user'] and password==params['password']):
            session['user']=username
            flash("Login success","info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger") 

    return render_template("admin.html")
@app.route('/logout')
@login_required
def logout():
    if 'user_type' in session:
        session.pop('user_type')
    logout_user()
    flash("Logout SuccessFul", "warning")
    return redirect(url_for('login'))

@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.upi_id
    print(code)
    data=Bookingpatient.query.filter_by(upi_id=code).first()
    return render_template("details.html",data=data)


@app.route('/addHospitalUser',methods=['POST','GET'])
def hospitalUser():
    if('user' in session and session['user']==params['user']):
                if request.method=="POST":
                    hcode=request.form.get('hcode')
                    email=request.form.get('email')
                    password=request.form.get('password')        
                    encpassword=generate_password_hash(password)  
                    hcode=hcode.upper()      
                    emailUser=Hospitaluser.query.filter_by(email=email).first()
                    if  emailUser:
                        flash("Email or upi_id is already taken","warning")
                
                    # db.engine.execute(f"INSERT INTO `hospitaluser` (`hcode`,`email`,`password`) VALUES ('{hcode}','{email}','{encpassword}') ")
                    query=Hospitaluser(hcode=hcode,email=email,password=encpassword)
                    db.session.add(query)
                    db.session.commit()

                    # my mail starts from here if you not need to send mail comment the below line
                
                    # mail.send_message('Govt Bed slot CENTER',sender=params['gmail-user'],recipients=[email],body=f"Welcome thanks for choosing us\nYour Login Credentials Are:\n Email Address: {email}\nPassword: {password}\n\nHospital Code {hcode}\n\n Do not share your password\n\n\nThank You..." )

                    flash("Data Sent and Inserted Successfully","warning")
                    return render_template("addHosUser.html")

    else:
        flash("Login and try Again","warning")
        return render_template("addHosUser.html")
    
@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')

@app.route('/hospitallogin', methods=['POST', 'GET'])
def hospitallogin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = Hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "info")
            

            return redirect('/addhospitalinfo')

        else:
            flash("Invalid Credentials", "danger")
            return render_template("hospitallogin.html")

    return render_template("hospitallogin.html")

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        
        # Perform the search operation on the database
        search_results = Bookingpatient.query.filter(
            Bookingpatient.pname.ilike(f'%{search_query}%') |
            Bookingpatient.pphone.ilike(f'%{search_query}%') |
            Bookingpatient.upi_id.ilike(f'%{search_query}%')
        ).all()
        
        return render_template("search_results.html", search_results=search_results)

    return render_template("search.html")


@app.route("/addhospitalinfo",methods=['POST','GET'])
@login_required
def addhospitalinfo():
    
    email=current_user.email
    posts=Hospitaluser.query.filter_by(email=email).first()
    code=posts.hcode
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()

    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        huser=Hospitaluser.query.filter_by(hcode=hcode).first()
        hduser=Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("Data is already Present you can update it..","primary")
            return render_template("hospitaldata.html")
        if huser:            
            # db.engine.execute(f"INSERT INTO `hospitaldata` (`hcode`,`hname`,`normalbed`,`hicubed`,`icubed`,`vbed`) VALUES ('{hcode}','{hname}','{nbed}','{hbed}','{ibed}','{vbed}')")
            query=Hospitaldata(hcode=hcode,hname=hname,normalbed=nbed,hicubed=hbed,icubed=ibed,vbed=vbed)
            db.session.add(query)
            db.session.commit()
            flash("Data Is Added","primary")
            return redirect('/addhospitalinfo')
            

        else:
            flash("Hospital Code not Exist","warning")
            return redirect('/addhospitalinfo')




    return render_template("hospitaldata.html",postsdata=postsdata)

@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
    posts=Hospitaldata.query.filter_by(id=id).first()
  
    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        # db.engine.execute(f"UPDATE `hospitaldata` SET `hcode` ='{hcode}',`hname`='{hname}',`normalbed`='{nbed}',`hicubed`='{hbed}',`icubed`='{ibed}',`vbed`='{vbed}' WHERE `hospitaldata`.`id`={id}")
        post=Hospitaldata.query.filter_by(id=id).first()
        post.hcode=hcode
        post.hname=hname
        post.normalbed=nbed
        post.hicubed=hbed
        post.icubed=ibed
        post.vbed=vbed
        db.session.commit()
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")

    # posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html",posts=posts)

@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    # db.engine.execute(f"DELETE FROM `hospitaldata` WHERE `hospitaldata`.`id`={id}")
    post=Hospitaldata.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Data Deleted","danger")
    return redirect("/addhospitalinfo")

@app.route("/trigers")
def trigers():
    query=Trig.query.all() 
    return render_template("trigers.html",query=query)



@app.route("/slotbooking", methods=['POST', 'GET'])
@login_required
def slotbooking():
    query1 = Hospitaldata.query.all()
    query = Hospitaldata.query.all()
    
    if request.method == "POST":
        upi_id = request.form.get('upi_id')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode')
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')
        
        check2 = Hospitaldata.query.filter_by(hcode=hcode).first()
        checkpatient = Bookingpatient.query.filter_by(upi_id=upi_id).first()
        
        if checkpatient:
            flash("Already UPI ID is registered", "warning")
            return render_template("booking.html", query=query, query1=query1)
        
        if not check2:
            flash("Hospital Code does not exist", "warning")
            return render_template("booking.html", query=query, query1=query1)
        

        code=hcode
        dbb = Hospitaldata.query.filter_by(hcode=hcode).first()
        bedtype = bedtype
        seat = 0
        
        if bedtype == "NormalBed":
            seat = dbb.normalbed
            print(seat)
            ar = Hospitaldata.query.filter_by(hcode=hcode).first()
            ar.normalbed = seat - 1
            db.session.commit()
            
        elif bedtype == "HICUBed":
            seat = dbb.hicubed
            print(seat)
            ar = Hospitaldata.query.filter_by(hcode=hcode).first()
            ar.hicubed = seat - 1
            db.session.commit()

        elif bedtype == "ICUBed":
            seat = dbb.icubed
            print(seat)
            ar = Hospitaldata.query.filter_by(hcode=hcode).first()
            ar.icubed = seat - 1
            db.session.commit()

        elif bedtype == "VENTILATORBed":
            seat = dbb.vbed
            ar = Hospitaldata.query.filter_by(hcode=hcode).first()
            ar.vbed = seat - 1
            db.session.commit()

        else:
            pass
        
        if seat > 0:
            res = Bookingpatient(upi_id=upi_id, bedtype=bedtype, hcode=hcode, spo2=spo2, pname=pname, pphone=pphone, paddress=paddress)
            db.session.add(res)
            db.session.commit()
            flash("Slot is Booked. Kindly visit the hospital for further procedures.", "success")
        else:
            flash("Something went wrong or no available beds.", "danger")
        
        return render_template("booking.html", query=query, query1=query1)
    
    return render_template("booking.html", query=query, query1=query1)





app.run(debug=True)
