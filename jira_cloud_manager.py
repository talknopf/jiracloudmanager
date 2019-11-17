# -*- coding: utf-8 -*-
#load dependencies
import os
import sys
import json
from jira import JIRA
from flask import Flask, request, Response, redirect
import rq_dashboard
import redis
from rq import Worker, Queue, Connection

import functools
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

sys.path.append('flows/')
sys.path.append('tools/')
sys.path.append('orchestration_flows/')
sys.path.append('github_flows/')

#a module to facilitate better work with google sso api
import google_auth

#import general function module
import jira_issue_toolbox as toolbox

#load logic modules
import doc_new_issues
import github_parsing_flow
import doc_update_issues
import jira_itissues
import jira_comment
import issue_update_flow
import issue_created_flow


# import jenkins_deployments
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

app = Flask(__name__)

#google auth
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY")
app.register_blueprint(google_auth.app)

#dashboard
@rq_dashboard.blueprint.before_request
def login_via_google_sso():
  if not google_auth.is_logged_in():
    return redirect("/google/login", code=302)

app.config.from_object(rq_dashboard.default_settings)
app.config['RQ_DASHBOARD_REDIS_URL'] = redis_url 
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/yentel-dashboard")

#route to catch webhook from Jira  for new issues
@app.route('/')
def home():
  if google_auth.is_logged_in():
    user_info = google_auth.get_user_info()
    print "A user just logged in to the dashboard" + json.dumps(user_info, indent=4)
    return redirect("/yentel-dashboard", code=302)
  else:
    return redirect("/google/login", code=302)
    
#logic flows start here
#route to catch webhook from Jira  for new issues
@app.route('/issue_created',methods=['POST'])
def function_sprint_new_issue_response():
  return issue_created_flow.new_issue_hook(request.data, jira)
  
#route to catch webhook from jira and react to the new project structure
@app.route('/issue_updated',methods=['POST'])
def function_sprint_update_response():
  username = request.args.get('user_id')
  if toolbox.should_exclude_request(request):
    return "200"
  else:
    return issue_update_flow.updated_issue_hook(request.data, jira, username)

#route to catch webhook for new issued from DOC project 
@app.route('/newdocproject',methods=['POST'])
def function_doc_new_issue_response():
  return doc_new_issues.new_doc_issue_hook(request.data, jira)

#route to catch webhook for new issued from DOC project 
@app.route('/updatedocproject',methods=['POST'])
def function_doc_update_issue_response():
  return doc_update_issues.doc_update_issue(request.data, jira)

#route to catch Github hooks (meeyaooo...)
@app.route('/github',methods=['POST'])
def function_github_response():
  # return github_parsing_flow.github_parsing_hook(request.data, jira, request.headers)
  return github_parsing_flow.github_main(request, jira)

#route to handle IT issues for the time being both new and updates
@app.route('/jiracomment',methods=['POST'])
def function_new_jira_comments_response():
  return jira_comment.new_comment_flow(request.data, jira)

if __name__ == '__main__':
  jirauser = str(os.environ.get('JIRAUSER'))
  jirapass = str(os.environ.get('JIRAKEY'))
  jiraserver = str(os.environ.get('JIRASERVER'))

  global jira
  jira = JIRA(basic_auth=(jirauser, jirapass), options={'server': jiraserver})

  port = int(os.environ.get('PORT', 80))
  print "app will run on port:", port
  app.run(host='0.0.0.0', port=port)
