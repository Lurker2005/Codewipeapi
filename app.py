import flask
import mysql.connector
from flask_mail import Mail,Message 
import random
import os
from dotenv import load_dotenv

load_dotenv()
app = flask.Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)
def sendmail(type,email):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Robotics26!",
        database="codewipe"
    )
    opt=random.randint(1000,9999)
    curser=con.cursor(dictionary=True)
    query="INSERT INTO otptable (email, otp, Purpose) VALUES (%s, %s, %s)"
    curser.execute(query, (email, opt, type))
    con.commit()
    curser.close()
    con.close()
    msg=Message(
        subject="OTP for "+type,
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body="Your OTP for "+type+" is "+str(opt)
    mail.send(msg)



@app.route("/login",methods=["POST"])
def login():
    data = flask.request.get_json()
    username = data.get("username")
    password = data.get("password")

    con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Robotics26!",
            database="codewipe"
    )
    cursor = con.cursor(dictionary=True)

    query = "SELECT * FROM usertable WHERE username=%s AND password=%s"
    cursor.execute(query, (username, password))

    user = cursor.fetchone()

    cursor.close()
    con.close()
    
    if user:
        email = user["email"]
        sendmail("Login",email)
        return "Otp Sent to the login email"
    else:
        return "Invalid Credentials"
    
@app.route("/verifyotp",methods=["GET","POST"])
def verifyotp():
    con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Robotics26!",
            database="codewipe"
    )
    data = flask.request.get_json()
    otp = data.get("otp")
    email = data.get("email")
    query = "SELECT * FROM otptable WHERE email=%s"
    cursor = con.cursor(dictionary=True)
    cursor.execute(query, (email,))
    record = cursor.fetchone()
    if(record["otp"] == otp):  
        if(record["Purpose"] == "Login"):
            query = "DELETE FROM otptable WHERE email=%s"
            cursor.execute(query, (email,))
            con.commit()
            cursor.close()
            con.close()
            return "Login Successful"
        else:
            query = "INSERT INTO usertable (email, Username, Phonenumber, password) SELECT email, Username, Phonenumber, password FROM registerpending WHERE email=%s"
            cursor.execute(query, (email,))
            
            query = "DELETE FROM registerpending WHERE email=%s"
            cursor.execute(query, (email,))
            query = "DELETE FROM otptable WHERE email=%s"
            cursor.execute(query, (email,))
            con.commit()
            cursor.close()
            con.close()
            return "Registration Successful"

    else:
        return "Invalid OTP"

@app.route("/register",methods=["POST"])
def register():
    data = flask.request.get_json()
    email = data.get("email")
    username= data.get("username")
    number= data.get("number")
    password = data.get("password")

    con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Robotics26!",
            database="codewipe"
    )
    cursor = con.cursor()

    query = "INSERT INTO registerpending (email, Username, Phonenumber, password) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (email, username, number, password))
    con.commit()
    cursor.close()
    con.close()
    sendmail("Registration",email)
    return "Registration email is Suceccfully sent to the email"


if __name__ == "__main__":
    app.run(debug=True)
