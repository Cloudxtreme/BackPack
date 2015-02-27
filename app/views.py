from flask import render_template, flash, redirect
from app import app
from flask import request

@app.route('/')
@app.route('/home')
def index():
  user= {'name': ''}
  return render_template('ion/index.html',
                        title='GottaBack - Home',
                        user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if (request.form['username']):
      user={'name':request.form['username']}
      return render_template('ion/index.html',
                        title='GottaBack - Home',
                        user=user)

    #              request.form['password']):
    #  return log_the_user_in(request.form['username'])
    else:
      error = 'Invalid username/password'
  return render_template('ion/login.html',
                        title='GottaBack - Log In',
                        ferror=error)
