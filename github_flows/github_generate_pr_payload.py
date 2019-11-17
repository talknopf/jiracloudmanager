import os
import sys
import json
from jira import JIRA
from flask import Flask, request
import re

sys.path.append('../tools/')

import jira_issue_toolbox as toolbox
import jira_connector as j


def derive_jira_id_from_payload(gh_payload, projects_to_check=['APPS','CORE'],jira=j.setup_jira_object()):
  #try and derive jira id from pr branch name
  if gh_payload['branch_name']:
    branch_name_upper = gh_payload['branch_name'].upper()
    for key in projects_to_check:
      if key in branch_name_upper:
        match = re.search('(^.*)([A-Z]{4}-\d+)(.*)', branch_name_upper)
        jira_key = match.group(2)
        issue = jira.issue(jira_key)
        if issue.key:
          return jira_key
  return False

def generate_payload(request, jira=j.setup_jira_object()):
  payload = {}
  try:
    data = json.loads(request.data)
  except Exception as e:
    print "json payload invalid "
    print e
    print data
    return "500"
  try:
    payload['action'] = data['action']
  except Exception as e:
    payload['action'] = False

  try:
    payload['merged'] = data['pull_request']['merged']
  except Exception as e:
    payload['merged'] = False

  try:
    payload['pr_title_string'] = data['pull_request']['title'] ,
  except Exception as e:
    payload['pr_title_string'] = False
    
  try:
    payload['github_assignee'] = data['assignee']['login']
  except Exception as e:
    payload['github_assignee'] = False

  try:
    payload['pull_request_api_url'] = data['pull_request']['_links']['self']['href']
  except Exception as e:
    payload['pull_request_api_url'] = False

  try:
    payload['pull_request_html_url'] = data['pull_request']['html_url']
  except Exception as e:
    payload['pull_request_html_url'] = False

  try:
    payload['branch_name'] = (data['pull_request']['head']['label']).split(":")[1]
  except Exception as e:
    payload['branch_name'] = 'master'

  jira_id_found = derive_jira_id_from_payload(payload)
  if jira_id_found:
    payload['linked_jira_issue'] = jira_id_found
  else:
    payload['linked_jira_issue'] = False
    
#Print out payload to improve debugability
  print "Parsing Github Hook with PR subject:", payload['pr_title_string']
  print (json.dumps(payload, sort_keys=True))

  return payload
