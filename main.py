import cv2
import sys
import os
import numpy as np
from face_recognition import face_encodings, face_locations, compare_faces, face_distance
from datetime import datetime, date
from keyboard import is_pressed
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL
from pandas import DataFrame
from werkzeug.utils import secure_filename

app = Flask(__name__)


app.config["Secret_Key"] = "6a79852e71abd3dc5e4d#"
#megrun_with_ngrok(app)
app.debug = True
app.secret_key = "AsdHahD12@!#@3@#@#554"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSORD'] = ''
app.config["MYSQL_DB"] = 'face pay'
app.config["SQLALCHEMY_DATABASE_URL"] = "http://localhost/phpmyadmin/db_structure.php?server=1&db=face+pay"
app.config["MYSQL CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)


@app.route("/")
def inde():
    return render_template("index.html")


@app.route("/register", methods=(["GET", "POST"]))
def register():
    # form = loginform()
    try:
        con = mysql.connection.cursor()
        print("Connected to database")
    except Exception as e:
        sys.exit(e)
    # cur = con.cursor()
    con.execute("SELECT * FROM register")
    data = DataFrame(data=con.fetchall())

    if request.method == "POST":
        Name = request.form['Name']
        Password = request.form["Password"]

        cur = mysql.connection.cursor()

        if Name in list(data[0]):
            if Password not in list(data[1]):
                flash("You need to log in")
                return render_template("index.html")
                flash('User already exist')
                return render_template('index.html')
            else:
                cur.execute("INSERT INTO register(usr_name,password) VALUES (%s,%s)",
                            (Name, Password))
                mysql.connection.commit()
                cur.close()
        else:
            flash("Both evoc-id does no match")
            # return render_template("login.html", output_data=data)
            # if cur.username != username:
            # flash("you writtern wrong evoc_id")

            flash("Submission-Successful")
            return render_template("image.html")
    return render_template("image.html")


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markEntry(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            d = date.today()
            f.writelines(f'\n{name},{d},{dtString}')


path = 'database_images'


@app.route("/start")
def detect_faces():
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_locations(imgS)
        encodesCurFrame = face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = compare_faces(encodeListKnown, encodeFace)
            faceDis = face_distance(encodeListKnown, encodeFace)
            # print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markEntry(name)

        cv2.imshow('Webcam', img)
        if is_pressed("esc"):
            return "Face is scanned"
            exit()
        cv2.waitKey(1)


# @app.route("/register")
# def registerUser():
#     # email = request.form.get("email")
#     return render_template("image.html")


# Upload images here
UPLOAD_FOLDER = "C:/Users/asus/Desktop/Practice/Face Detection"
ALLOWED_EXTENSIONS = {'jpg', 'png'}
id = 1

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Providing the route to an html
@app.route('/upload', methods=["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No Flash Apart")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == '':
            flash("No File Selected")
            return redirect(request.url)
        else:
            # if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            file.filename = f"{id}.png"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO register(image_path) VALUES(%s)", (filename,))
            cur.connection.commit()
            cur.close()
            id += 1
            # return redirect(url_for('uploaded_file', filename=filename))
    # return render_template("admin.html")



if __name__ == '__main__':
    print("Encoding has been started please wait a few minutes :)")
    images = []
    classNames = []
    myList = os.listdir(path)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    # print(classNames)
    encodeListKnown = findEncodings(images)
    print('Encoding Complete')
    # detect_faces(encodedList)
    app.run(debug=True)
