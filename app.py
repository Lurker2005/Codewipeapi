import flask
import mysql.connector
from flask_mail import Mail,Message 
import random
import os
from dotenv import load_dotenv

load_dotenv()
app = flask.Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = "noreply@bharatwipe.online"

mail = Mail(app)
def sendmail(type, email):
    con = mysql.connector.connect(
        host="localhost",
        user="codewipe",
        password="Robotics26!",
        database="codewipe"
    )

    cursor = con.cursor(dictionary=True)

    # Generate 6-digit OTP
    opt = random.randint(100000, 999999)

    # Check if OTP already exists for email
    cursor.execute("SELECT * FROM otptable WHERE email=%s", (email,))
    existing = cursor.fetchone()

    if existing:
        # Update existing OTP
        update_query = "UPDATE otptable SET otp=%s, Purpose=%s WHERE email=%s"
        cursor.execute(update_query, (opt, type, email))
    else:
        # Insert new OTP
        insert_query = "INSERT INTO otptable (email, otp, Purpose) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (email, opt, type))

    con.commit()
    cursor.close()
    con.close()

    msg = Message(
        subject="OTP for " + type,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email]
    )

    msg.body = f"Your OTP for {type} is {opt}"

    msg.html = f"""
    <html>
    <body style="font-family: Arial; background:#f4f6f9; padding:20px;">
        <div style="max-width:500px; margin:auto; background:white; padding:30px; border-radius:10px;">
            <h2 style="color:#2e7d32; text-align:center;">CodeWipe Verification</h2>
            <p>Your OTP for <strong>{type}</strong> is:</p>
            <div style="text-align:center; margin:25px 0;">
                <span style="font-size:28px; font-weight:bold; color:white; background:#2e7d32; padding:15px 25px; border-radius:8px; letter-spacing:4px;">
                    {opt}
                </span>
            </div>
            <p style="font-size:14px; color:#777;">
                This OTP is valid for limited time.
            </p>
        </div>
    </body>
    </html>
    """

    mail.send(msg)
# def sendmail(type,email):
#     con = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Robotics26!",
#         database="codewipe"
#     )
#     opt=random.randint(100000,999999)
#     curser=con.cursor(dictionary=True)
#     query="INSERT INTO otptable (email, otp, Purpose) VALUES (%s, %s, %s)"
#     curser.execute(query, (email, opt, type))
#     con.commit()
#     curser.close()
#     con.close()
#     msg=Message(
#         subject="OTP for "+type,
#         sender=app.config['MAIL_USERNAME'],
#         recipients=[email]
#     )
#     msg.body = f"Your OTP for {type} is {opt}"

#     msg.html = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">
#             <div style="max-width:500px; margin:auto; background:white; padding:30px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
            
#             <h2 style="color:#2e7d32; text-align:center;">CodeWipe Security Verification</h2>
            
#             <p style="font-size:16px; color:#333;">
#                 Hello,
#             </p>
            
#             <p style="font-size:16px; color:#333;">
#                 Your OTP for <strong>{type}</strong> is:
#             </p>
            
#             <div style="text-align:center; margin:25px 0;">
#                 <span style="font-size:28px; font-weight:bold; color:white; background:#2e7d32; padding:15px 25px; border-radius:8px; letter-spacing:4px;">
#                 {opt}
#                 </span>
#             </div>
            
#             <p style="font-size:14px; color:#777;">
#                 This OTP is valid for a limited time. Do not share it with anyone.
#             </p>

#             <hr style="margin:20px 0;">

#             <p style="font-size:12px; color:#aaa; text-align:center;">
#                 © 2026 CodeWipe | Secure Data Erasure Platform
#             </p>

#             </div>
#         </body>
#         </html>
#         """
#     mail.send(msg)



@app.route("/login",methods=["POST"])
def login():
    data = flask.request.get_json()
    email = data.get("email")
    password = data.get("password")

    con = mysql.connector.connect(
            host="localhost",
            user="codewipe",
            password="Robotics26!",
            database="codewipe"
    )
    cursor = con.cursor(dictionary=True)

    query = "SELECT * FROM usertable WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))

    user = cursor.fetchone()

    cursor.close()
    con.close()
    
    if user:
        sendmail("Login",email)
        return "Otp Sent to the login email"
    else:
        return "Invalid Credentials"
    
@app.route("/verifyotp",methods=["GET","POST"])
def verifyotp():
    con = mysql.connector.connect(
            host="localhost",
            user="codewipe",
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
    if not record:
        return "OTP Expired or Not Found"
    if(str(record["otp"]) == str(otp)):  
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
    number= data.get("phonenumber")
    password = data.get("password")

    con = mysql.connector.connect(
            host="localhost",
            user="codewipe",
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
    app.run(host="0.0.0.0", port=5000)
