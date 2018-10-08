# -*- coding: utf-8 -*-
#load dependencies
import os
import sys
import json
from jira import JIRA
from flask import Flask, request

#load logic modules
import jira_updated_issue
import jira_new_issue
import github_parsing_flow

# import jenkins_deployments

app = Flask(__name__)

#route to catch webhook from Jira for new issues
@app.route('/newissue',methods=['POST'])
def function_new_response():
  return jira_new_issue.new_issue_hook(request.data, jira)

#route to catch webhook from Jira for updated issues will also ignore issues generater by the service
@app.route('/updatedissue',methods=['POST'])
def function_update_response():
  jira_service_user = str(os.environ.get('JIRAUSER'))
  username = request.args.get('user_id')
  if username == jira_service_user:
    print 'Since update was triggered from this service so will be ignore it'
    return '200'
  else:
    return jira_updated_issue.updated_issue_hook(request.data, jira)

if __name__ == '__main__':
  jirauser = str(os.environ.get('JIRAUSER'))
  jirapass = str(os.environ.get('JIRAKEY'))
  jiraserver = str(os.environ.get('JIRASERVER'))

  global jira
  jira = JIRA(basic_auth=(jirauser, jirapass), options={'server': jiraserver})

  port = int(os.environ.get('PORT', 80))
  print "app will run on port:", port
  app.run(host='0.0.0.0', port=port, debug=True)
