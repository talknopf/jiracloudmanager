import os
import sys
import json
from jira import JIRA

sys.path.append('../tools/')

import jira_issue_toolbox as toolbox
import generate_payload_by_id
import jira_connector as j

def link_to_doc_issue(jira_key, jira=j.setup_jira_object()):
  #this function will verify that an issue with the requirment for a doc issue 
  #has a valid doc issue with a link to it
  #list of project codes we act upon
  payload = generate_payload_by_id.generate_payload(jira_key)
  projects_to_check = ['SDK' ,'CLD' ,'PROD','APPS','CORE']

  if toolbox.requires_documentation(payload) and toolbox.issue_within_projects(payload, projects_to_check):
    linked_doc_issues = toolbox.check_for_linked_issue_by_project(payload['issue_key'], jira, 'DOC')
    if not linked_doc_issues: #if false means no linked doc issues were found and will create new one
      new_issue_dict = {'project': {'key': 'DOC'},
                        'summary': "Document: " + payload['jira_summary'] ,
                        'description': payload['jira_description'] ,
                        'issuetype': {'name' : 'Story'},
                        'priority' : {'name' : payload['jira_priority']},
                        'customfield_10900': {'value': payload['source']}, 
                        'customfield_10004': payload['epic'],
                        'customfield_11000': payload['release_notes']
                        }
      print "will open a new DOC issue with following parameters:"
      print (json.dumps(new_issue_dict, sort_keys=True))
      
      new_issue = jira.create_issue(fields=new_issue_dict)
      print "New jira issue created:", new_issue.key

      print "Will now link:", jira_key, "to:", new_issue.key
      jira.create_issue_link(type='Problem/Incident', inwardIssue=jira_key, outwardIssue=new_issue.key)
      
      print "Will now assign ", new_issue.key ," to Docs team"
      jira.assign_issue(new_issue, 'docs')

    else:
      print payload['issue_key'], "Is marked as Doc Update required but already has linked DOC issue"
      transition_linked_doc_issues(linked_doc_issues, payload, jira)
      terminate_wont_do_doc_issues(linked_doc_issues, payload, jira)

def transition_linked_doc_issues(linked_doc_issues, payload, jira):
  status_to_act_on = ['In Review' , 'Testing' , 'Tested' , 'Done', 'Pushed', 'Deployed','Published']
  if payload['status'] in status_to_act_on:
    for linked_issue in linked_doc_issues:
      linked_issue_obj = jira.issue(linked_issue)
      linked_issue_status = linked_issue_obj.fields.status.name #raw['fields']['status']['name']
      print 'Checking linked issue:', str(linked_issue) , ' the status of it is:', linked_issue_status
      
      if linked_issue_status != 'Done' and linked_issue_status == 'To Do':
        print "Changing doc issue status since parent issue requires it"
        toolbox.transition_to_status(linked_issue, 'Ready for dev', jira)

def terminate_wont_do_doc_issues(linked_doc_issues, payload, jira):
  status_to_act_on = ['Resolved - Won\'t fix' , 'Duplicate']
  if payload['status'] in status_to_act_on:
    for linked_issue in linked_doc_issues:
      linked_issue_obj = jira.issue(linked_issue)
      linked_issue_status = linked_issue_obj.fields.status.name #raw['fields']['status']['name']
      print 'Checking linked issue:', str(linked_issue) , ' the status of it is:', linked_issue_status
      
      if linked_issue_status != payload['status']:
        print "Changing doc issue status since parent issue requires it"
        toolbox.transition_to_status(linked_issue, payload['status'], jira)
