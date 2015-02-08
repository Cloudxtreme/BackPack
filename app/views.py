from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
  user= {'nickname': 'GreatLeader'}
  return render_template('ion/index.html',
                        title='GottaBack - Home',
                        user=user)