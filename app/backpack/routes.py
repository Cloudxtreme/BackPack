import chartkick
import httplib2, json, argparse, StringIO, tarfile
from flask import render_template, flash, redirect, request, url_for, session, make_response, send_file, Response
from . import backpack
from flask.ext.login import login_user, current_user, login_required, logout_user
from ..models import User, db
from apiclient import errors
from apiclient.discovery import build
from datetime import datetime, timedelta
import dateutil.parser
import logging
from oauth2client import client, tools

@backpack.route('/')
@backpack.route('/home')
def index():
  return render_template('ion/index.html',
                        title='BackPack - Home')

@backpack.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    if (request.form.get('email', None)):
      user = User.query.filter_by(email=request.form['email']).first()      
      if user is None or not user.verify_password(request.form['password']):
        flash('Invalid username/password.')
        return redirect(url_for('.login'))
      login_user(user, remember=True)
      if current_user.is_admin:
        return redirect(url_for('.admin', username=user.username))
      else:
        return redirect(url_for('.user', username=user.username))
  return render_template('ion/login.html',
                        title='BackPack - Home')

@backpack.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out" )
    return redirect('login')

@backpack.route('/admin/config', methods=['GET', 'POST'])
@login_required
def config():
  if not current_user.is_admin:
    flash("You're attempt has been recorded.")
    redirect('login')
  if request.method == 'POST':
    usernames = request.form.getlist('username')
    hostnames = request.form.getlist('host')
    backups = request.form.getlist('backup')
    exclusions = request.form.getlist('exclude')
    text=''
    for i in range(len(usernames)):
      if usernames[i] != '' and hostnames[i] != '' and backups[i] != '':
        text += usernames[i] + " " + hostnames[i] + " "
        text += backups[i].replace(" ", ":") + " " + exclusions[i].replace(" ", ":")
        text += "\n"
    response = make_response(text)
    response.headers["Content-Disposition"] = "attachment; filename=backpack.conf"
    return response
  return render_template('ion/config.html',
                        title='BackPack - Config',
                        username=current_user.username)

@backpack.route('/user/<username>/backups')
@login_required
def backup(username):
  user = current_user
  if 'credentials' not in session:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  http_auth = credentials.authorize(httplib2.Http())
  drive = build('drive', 'v2', http_auth)
  backups = drive_backupfolder(username, drive)
  files = drive_files(backups['items'][0]['id'], drive)
  #file = drive_folder_links(drive, files['items'])
  return render_template('ion/backup.html',
                          title='BackPack - Backups',
                          username=current_user.username,
                          backups=files['items'])

@backpack.route('/admin/stats')
@login_required
def stats():
  stats=[]
  user = current_user
  if 'credentials' not in session:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  http_auth = credentials.authorize(httplib2.Http())
  drive = build('drive', 'v2', http_auth)
  users = drive_files('root', drive)
  for user in users['items']:
    if user.get('mimeType') == 'application/vnd.google-apps.folder':
      print user.get('title')
      children = drive_folder_links(drive, user.get('title'))
      size = 0
      if children is None:
        break
      for child in children:
        size += child.get('fileSize')
      stats.append[user.get('title'), size]
  stats = [['john', 5400], ['victor', 1200]]
  print 'Stats ',stats
  return render_template('ion/stats.html',
                          title='BackPack - Statistics',
                          username=current_user.username,
                          stats=stats)

@backpack.route('/user/backups/download/<folder>/<parent>')
@login_required
def download(folder, parent):
  user = current_user
  if 'credentials' not in session:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  http_auth = credentials.authorize(httplib2.Http())
  drive = build('drive', 'v2', http_auth)
  
  files = []
  tar = tarfile.open('/home/user/Downloads/'+parent+'.tar', mode="w")
  children = drive_folder_links(drive, folder)
  for child in children:
    content = download_file(drive, child)
    if content == None:
      print child.get('title')+": Download fail\n"
    else:
      #d = dict()
      #d['title'] = child.get('title')
      #d['content'] = content
      #files.append(d)
      #content = content.encode('utf-8')
      info = tarfile.TarInfo(name=child.get('title'))
      info.size=len(content.buf)
      tar.addfile(tarinfo=info, fileobj=content) 
  tar.close()
  #return Response(tar, mimetype="application/x-tar")
  return redirect(url_for('.backup', username=user.username))

@backpack.route('/user/<username>')
@login_required
def user(username):
  user = current_user
  if 'credentials' not in session:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(url_for('.oauth2callback'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    drive = build('drive', 'v2', http_auth)
    changes = drive_listchanges(drive)
    return render_template('ion/user.html',
                          title='BackPack - ' + user.username,
                          username=user.username,
                          changes=changes)

@backpack.route('/admin')
@login_required
def admin():
  admin = current_user
  if 'credentials' not in session:
    return redirect(url_for('.oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(url_for('.oauth2callback'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    drive = build('drive', 'v2', http_auth)
    changes = drive_listchanges(drive)
    return render_template('ion/admin.html',
                          title='BackPack - ' + admin.username.upper(),
                          username=admin.username,
                          changes=changes)

@backpack.route('/oauth2callback')
def oauth2callback():
  CLIENTSECRETS_LOCATION = '../client_secret.json'
  SCOPES = (
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
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
      if current_user.is_admin:
        return redirect(url_for('.admin'))
      else:
        return redirect(url_for('.user', username=current_user.username))

def drive_listchanges(service):
  changes = service.changes().list().execute()
  result = []

  for change in changes.get('items'):
    current = {}
    if change.has_key('file'):
      current['type'] = change['file']['mimeType']
      current['title'] = change['file']['title']
      current['deleted'] = change['file']['labels']['trashed']
      current['creationDate'] = dateutil.parser.parse(change['file']['createdDate'])
      current['modificationDate'] = dateutil.parser.parse(change['file']['modifiedDate'])
      current['user'] = change['file']['lastModifyingUserName']
      result.append(current)
  return reversed(result)

def drive_backupfolder(name, service):
  query = "'root' in parents and mimeType = 'application/vnd.google-apps.folder' and title contains '" + name.lower()+"'"
  return service.files().list(q=query).execute()

def drive_files(parent, service):
  query = "'"+parent+"' in parents"
  try:
    return service.files().list(q=query).execute()
  except:
    return {}

def drive_folder_links(service, folder):
  '''
  Return append the children info of the given folder id
  '''
  try:
    children = drive_files(folder, service).get('items')  
    return children
  except:
    return None
def download_file(service, file):
  """Download a file's content.
  Args:
            service: Drive API service instance.
            drive_file: Drive File instance.

  Returns:
            File's content if successful, None otherwise.
  """
  print "Trying downloadUrl\n"
  download_url = file.get('downloadUrl')
  if download_url:
    resp, content = service._http.request(download_url)
    if resp.status == 200:
      print 'Status: %s' % resp
      buffer = StringIO.StringIO()
      buffer.write(content)
      buffer.seek(0)
      return buffer
    else:
      print 'An error occurred: %s' % resp
      return None
  else:
    print 'No url found'
    return None
