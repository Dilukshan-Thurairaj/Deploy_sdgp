import pickle
import os
import json
import sys
import numpy as np
import mysql.connector


from flask_mysqldb import MySQL
from flask import Flask, flash, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine

import sqlite3
from flask import request

from flask import Flask,session, request, render_template, jsonify


app = Flask(__name__)
app.secret_key = 'secret_key'


# database
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://studentprogresspro_user:Ubp7bK1QvDidST7YjWcsQ4SW6Pgk9Jol@dpg-cgl5ov64dad69r60cqs0-a.singapore-postgres.render.com/studentprogresspro"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#Connection
engine = create_engine('postgresql://studentprogresspro_user:Ubp7bK1QvDidST7YjWcsQ4SW6Pgk9Jol@dpg-cgl5ov64dad69r60cqs0-a.singapore-postgres.render.com/studentprogresspro')

connection = engine.raw_connection()

@app.route('/')
def loginpage():
    return render_template('login.html')
 
@app.route('/', methods=['POST'])
def login():
    
    username = request.form['username']
    password = request.form['password']

    
    c = connection.cursor()

    c.execute('SELECT * FROM public."user" WHERE username=%s AND password=%s',(username, password))
    row = c.fetchone()
    
    if row:
        c1 = connection.cursor()
        c1.execute('SELECT username, password FROM public."user" WHERE username=%s AND password=%s',(username, password))
        row1 = c1.fetchone()
        username, password = row1

        session['username'] = username

        return redirect('/home')
    
    else:
        
        flash("Enter details are wrong! Please check again")
        
        return redirect('/')

    return render_template('login.html')

@app.route('/register')
def signupPage():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    c1 = connection.cursor()

    c1.execute('SELECT username FROM public."user"')
    rows1 = c1.fetchall()

    usernameHas = True
    
    usernames = [row1[0] for row1 in rows1]

    for eachUsername in usernames:
        if eachUsername == username:
            usernameHas = False
            flash("This username is already in use")
            return redirect('/register')

    if usernameHas:
        c1.execute('INSERT INTO public."user" (username, password) VALUES (%s, %s)', (username, password))
        connection.commit()
        return render_template('login.html')

    return render_template('register.html')


@app.route('/home')
def home():   
    #Changed
    return render_template('homePage.html')

@app.route('/quiz')
def quiz():   
    return render_template('quiz.html')

@app.route('/testo1')
def testo1():

    c = connection.cursor()

    c.execute('SELECT * FROM public.testomonial ORDER BY "userID" DESC LIMIT 6')
    # columns = [description[0] for description in c.description]
    data = c.fetchall()
    
    reversed_data = []
    for i in range(len(data)-1, -1, -1):
        reversed_data.append(data[i])
    
    print(len(data))
    print(type(data))
    lenArr = len(data)
    # Print the data
    # for row in data:
    #     print(row)

    return render_template('testo2.html', reversed_data=reversed_data, lenArr=lenArr)


@app.route('/testo11', methods=['POST'])
def testoData():

    username = session.get('username')
    feedback = request.form['feedback']
    rating = request.form['rating']
    
    
    print(username)
    
    c = connection.cursor()
    c.execute('INSERT INTO public.testomonial (username, review, rating) VALUES (%s, %s, %s)', (username, feedback, rating))
    #Committing to the connection
    connection.commit()

    return redirect('/testo1')
    
    

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

#testcomment

@app.route('/test', methods=['POST'])
def test():
    output = request.get_json()
    print(output) # This is the output that was stored in the JSON within the browser
    print(type(output))
    result = json.loads(output) #this converts the json output to a python dictionary
    print(result) # Printing the new dictionary
    keys = list(result.keys())
    firstKey = keys[0]
    firstValue = result[firstKey]
    print(firstValue)
    
    import pickle

    with open('model_pickle_final.h5','rb') as f:
     mod =  pickle.load(f)
     
    # print(myarray)
    temp = mod.predict([firstValue])
    print(temp)
    #test comment added 
    arr_str = np.array2string(temp)

    # Print string representation of numpy array
    print(type(arr_str))
    
    
    session['mark'] = arr_str
    session['behav_Arr']=firstValue
 
     
    return jsonify({'arr_str':arr_str})
    

@app.route('/tips')
def tips():
    mark = session.pop('mark', None)
    print(mark)
    

    behav_Arr= session.pop('behav_Arr',None)
    print(behav_Arr)
    return render_template('tips.html', mark=mark, behav_Arr=behav_Arr)


if __name__ == "__main__":
    app.run(port= 8000, debug=True)
