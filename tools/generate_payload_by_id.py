# -*- coding: utf-8 -*-
import os
import sys
import json
import jira_issue_toolbox as toolbox
from jira import JIRA
import jira_connector as j

def generate_payload(jira_key, jira=j.setup_jira_object()):
  issue = jira.issue(jira_key)
  #normalize variables to avoid corruption
  data = {}
  data['issue'] = issue.raw
  try:
    payload = { 'status' : data['issue']['fields']['status']['name'] , 
                'issue_key' : data['issue']['key'],
                'labels' : data['issue']['fields']['labels'] ,
                'project_name' : data['issue']['fields']['project']['key'] ,
                'jira_summary' : data['issue']['fields']['summary'],
                'jira_description' : toolbox.force_to_unicode(data['issue']['fields']['description']) ,
                'jira_priority' : data['issue']['fields']['priority']['name'] ,
              }
  except TypeError:
    print "Json Body is missing required values, will stop and return 500"
    print (json.dumps(data, sort_keys=True))
    return "json error"
  try:
    payload['reporter'] = data['issue']['fields']['reporter']['name']
  except Exception as e:
    payload['reporter'] = ''

  try:
    payload['reporter_email'] = data['issue']['fields']['reporter']['emailAddress']
  except Exception as e:
    payload['reporter_email'] = 'nobody@cloudinary.com'

  try:
    payload['assignee_email'] = data['issue']['fields']['assignee']['emailAddress']
  except Exception as e:
    payload['assignee_email'] = 'nobody@cloudinary.com'
  
  try:
    payload['assignee'] = data['issue']['fields']['assignee']['name']
  except Exception as e:
    payload['assignee'] = 'Nobody'

  try:
    payload['issuetype'] = data['issue']['fields']['issuetype']['name']
  except Exception as e:
    payload['issuetype'] = 'Generic'

  #check if any documentation impact
  try:
    payload['docs_impact'] = data['issue']['fields']['customfield_11800']['value']
  except TypeError:
    payload['docs_impact'] = False
  
  try:
    payload['documentation'] = data['issue']['fields']['customfield_12043']['value']
  except TypeError:
    payload['documentation'] = False

  #check if any documentation impact
  try:
    payload['release_notes'] = data['issue']['fields']['customfield_11000']['value']
  except Exception as e:
    payload['release_notes'] = 'None'

  #try to get linked issus, if found
  try:
    payload['linked_issue_keys'] = [issue_link['outwardIssue']['key'] for issue_link in data['issue']['fields']['issuelinks']]
  except (IndexError, KeyError):
    payload['linked_issue_keys'] = []

  #try to get linked issus, if found
  try:
    payload['linked_issue_tree'] = data['issue']['fields']['issuelinks']
  except (IndexError, KeyError):
    payload['linked_issue_tree'] = False

  #check if the new issue requires qa
  try:
    payload['qa_required'] = data['issue']['fields']['customfield_11700']['value']
  except Exception as e:
    payload['qa_required'] = False

#check if the new issue requires qa
  try:
    payload['manual_qa'] = data['issue']['fields']['customfield_12042']['value']
  except Exception as e:
    payload['manual_qa'] = False

  #check if issue has a components list (some projects might not have it)
  try:
    payload['components'] = [comp_name['name'] for comp_name in data['issue']['fields']['components']]
  except Exception as e:
    payload['components'] = 'Not set'

  #check the source of the jira issue
  try:
    payload['source'] = data['issue']['fields']['customfield_10900']['value']
  except Exception as e:
    payload['source'] = 'Not set'

  #check the sdk impact of the issue
  try:
    payload['sdk_impact'] = data['issue']['fields']['customfield_12002']['value']
  except Exception as e:
    payload['sdk_impact'] = False

  try:
    payload['sdk_link'] = data['issue']['fields']['customfield_12044']['value']
  except Exception as e:
    payload['sdk_link'] = False

  #check if issue has a fixversion list (some projects might not have it)
  try:
    payload['fixversion'] = [i['name'] for i in data['issue']['fields']['fixVersions']]
  except Exception as e:
    payload['fixversion'] = []
  
  # check the epic of the jira issue
  try:
    payload['epic'] = data['issue']['fields']['customfield_10004']
  except Exception as e:
    payload['epic'] = 'Not set'
  
  #add the issues comment bodies to the payload
  try:
    payload['issue_comments'] = [comment['body'] for comment in issue.raw['fields']['comment']['comments']]
  except Exception as e:
    payload['issue_comments'] = 'No comments'

    #check if any documentation impact
  try:
    payload['mar_cs_ops'] = data['issue']['fields']['customfield_11987']['name']
  except Exception as e:
    payload['mar_cs_ops'] = 'Not set'

  try:
    payload['it_systems_list'] = data['issue']['fields']['customfield_11916']
  except Exception as e:
    payload['it_systems_list'] = 'Not set'

  try:
    payload['parsed_components'] = toolbox.convert_components_to_set(payload['components'])
  except Exception as e:
    print e
    payload['parsed_components'] = []

  #print out the payload to improve debugability
  # print "Parsing Jira issue", payload['issue_key']
  # print(json.dumps(payload, sort_keys=True))

  return payload

# if __name__=='__main__':
#   print generate_payload()