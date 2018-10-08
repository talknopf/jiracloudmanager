# -*- coding: utf-8 -*-
import os
import sys
import json

def generate_payload(data):
  #normalize variables to avoid corruption
  try:
    payload = { 'reporter' : data['issue']['fields']['reporter']['name'] , 
                'status' : data['issue']['fields']['status']['name'] , 
                'issue_key' : data['issue']['key'],
                'labels' : data['issue']['fields']['labels'] ,
                'project_name' : data['issue']['fields']['project']['key'] ,
                'jira_summary' : data['issue']['fields']['summary'],
                'jira_description' : data['issue']['fields']['description'] ,
                'jira_priority' : data['issue']['fields']['priority']['name'] ,
              }
  except TypeError:
    #if any other structure will be posted to this service it wont accept and return 500
    #this may serve as a layer of security and both a filter for data
    print "Json Body is missing required values, will stop and return 500"
    print (json.dumps(data, sort_keys=True))
    return "json error"
  #since not all fields exist on some projects, will try to exract them from request payload
  #if none is found will set som sort of verbal string 
  try:
    payload['assignee'] = data['issue']['fields']['assignee']['name']
  except Exception as e:
    payload['assignee'] = 'Nobody'

  try:
    payload['issuetype'] = data['issue']['fields']['issuetype']['name']
  except Exception as e:
    payload['issuetype'] = 'Generic'

  #load customfield example
  try:
    payload['docs_impact'] = data['issue']['fields']['customfield_XXXXX']['value']
  except TypeError:
    payload['docs_impact'] = 'None'

  #load linked issues which are a list of data structures within the payload
  try:
    payload['linked_issue_keys'] = [issue_link['outwardIssue']['key'] for issue_link in data['issue']['fields']['issuelinks']]
  except (IndexError, KeyError):
    payload['linked_issue_keys'] = []

  #check if issue has a fixversion list (some projects might not have it)
  try:
    payload['fixversion'] = [i['name'] for i in data['issue']['fields']['fixVersions']]
  except Exception as e:
    payload['fixversion'] = []
  
  #check the epic of the jira issue
  try:
    payload['epic'] = data['issue']['fields']['customfield_10004']['value']
  except Exception as e:
    payload['epic'] = 'Not set'

  #add the issues comment bodies to the payload
  #consider if using the raw request way since 
  #it may certain delay as the request depends on the jira server availability
  try:
    payload['issue_comments'] = [comment['body'] for comment in issue.raw['fields']['comment']['comments']]
  except Exception as e:
    payload['issue_comments'] = 'No comments'

    #check if any documentation impact
  try:
    payload['mar_cs_ops'] = data['issue']['fields']['customfield_11987']['name']
  except Exception as e:
    payload['mar_cs_ops'] = 'Not set'

  #print out the payload to improve debugability
  print "Parsing Jira issue (",payload['project_name'],")", payload['issue_key']
  print (json.dumps(payload, sort_keys=True))

  return payload

if __name__=='__main__':
	print generate_payload()