from flask import render_template, flash, redirect
from flask import request
from . import backpack

@backpack.route('/')
@backpack.route('/home')
def index():
  user= {'name': ''}
  return render_template('ion/index.html',
                        title='GottaBack - Home',
                        user=user)

@backpack.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if (request.form['username']):
      user={'name':request.form['username']}
      return render_template('ion/index.html',
                        title='GottaBack - Home',
                        user=user)

  # else:
  #   error = 'Invalid username/password'
  #return render_template('ion/login.html',
   #                     title='GottaBack - Log In',
   #                     ferror=error)

#TODO check if the username already exists
#Validate password for 6+ characters, lower/upper/numeric
'''
@backpack.route('/register', methods=['GET', 'POST'])
def register():
  error = None  
  return render_template('ion/register.html',
                        title='GottaBack - Register',
                        ferror=error)

@backpack.route('/user/<username>')
def user(username):
  return render_template('ion/user.html',
                        title='GottaBack - <username>',
                        username=username)
'''