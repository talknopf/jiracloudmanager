# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA
import jira_generate_payload
import jira_issue_toolbox
import team_members

def new_issue_hook(request_json_payload, jira):
  data = json.loads(request_json_payload)
  payload = jira_generate_payload.generate_payload(data)
  
  #invoke the teams structure module
  org_teams = team_members.load_team_members()
  
  #configure jira issue object
  issue = jira.issue(payload['issue_key'])  
  transitions = jira.transitions(issue)

  #set the source by the owner's team
  jira_issue_toolbox.set_source_by_owner(payload, jira)

  #open linked issue if conditions allow it
  jira_issue_toolbox.open_linked_issue(payload, jira)

  #enforce somthing on this issue
  jira_issue_toolbox.enforce_field_on_issue(payload, jira)

  #this is an example for transitioning the issue status based on: 
  #the content of the component field
  #and reporting user is a memeber of the QA team

  if ("component" in payload['components'] ) and payload['assignee'] == 'developer name' and payload['status'] == 'To Do' and payload['issuetype'] == 'Bug' and (member in payload['reporter'] for member in cld_team['QA']):
    print "Since jira Bug issue components contains new_media_library or Media Library will move to R&D:", payload['issue_key']
    #change status to ready for dev
    for t in transitions: 
      if t['name']=='Ready for dev':
        jira.transition_issue(issue, t['id'])
    #assign issue to rnd
    jira.assign_issue(issue, 'R&D') 

  #when logic flow is done, return 200
  return "200"

if __name__=='__main__':
	new_issue_hook()