import httplib2, json, argparse
from flask import render_template, flash, redirect, request, url_for, session
from . import backpack
from drive import drive_listchanges
from flask.ext.login import login_user, current_user
from ..models import User
from apiclient import errors
from apiclient.discovery import build
from datetime import datetime, timedelta
from oauth2client import file, client, tools

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
    if (request.form.get('email', None)):
      user = User.query.filter_by(email=request.form['email']).first()      
      if user is None or not user.verify_password(request.form['password']):
        flash('Invalid username/password.')
        return redirect(url_for('.login'))

      login_user(user, True)
      return redirect(url_for('.user', username=user.username))

  return render_template('ion/login.html',
                        title='GottaBack - Home')

@backpack.route('/user/<username>')
def user(username):
  user = User.query.filter_by(username=username).first_or_404()
  if 'credentials' not in session:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(url_for('.oauth2callback'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    drive = build('drive', 'v2', http_auth)
    changes = drive_listchanges(drive)
    print "\n Changes: \n", changes
    return render_template('ion/user.html',
                        title='GottaBack - ' + username,
                        username=username,
                        changes=changes)

@backpack.route('/oauth2callback')
def oauth2callback():
  CLIENTSECRETS_LOCATION = '../client_secret.json'
  SCOPES = (
    'https://www.googleapis.com/auth/drive.readonly.metadata',
    'https://www.googleapis.com/auth/admin.reports.audit.readonly',
    'https://www.googleapis.com/auth/admin.reports.usage.readonly',
  )
  flow = client.flow_from_clientsecrets(
      CLIENTSECRETS_LOCATION,
      SCOPES,
      redirect_uri=url_for('.oauth2callback', _external=True)
  )
  if 'code' not in request.args:
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)
  else:
      auth_code = request.args.get('code')
      credentials = flow.step2_exchange(auth_code)
      session['credentials'] = credentials.to_json()
      return redirect(url_for('.user', username=current_user.username))


def drive_listchanges(service):
  changes = service.changes().list().execute()
  print changes['items']
  result = []
  for change in changes['items']:
    current = {}
    if change.has_key('file'):
      current['type'] = change['file']['mimeType']
      current['title'] = change['file']['title']
      current['deleted'] = change['deleted']
      current['modificationDate'] = change['modificationDate']
      current['user'] = change['file']['lastModifyingUserName']
      result.append(current)

  return result