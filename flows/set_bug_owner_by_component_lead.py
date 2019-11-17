# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA

sys.path.append('../tools/')

import jira_issue_toolbox as toolbox
import generate_payload_by_id
import jira_connector as j

def bug_set_assignees_component_lead(jira_key, jira=j.setup_jira_object()):
  projects_to_check = ['CLD' ,'SDK','CORE', 'APPS']
  payload = generate_payload_by_id.generate_payload(jira_key)
  
  if 'Not set' in payload['components']:
    return False

  if toolbox.issue_within_projects(payload, projects_to_check) and (toolbox.issue_is_bug(payload) or toolbox.issue_is_task(payload)):
    # print payload['issue_key'], 'Will allocate bug to component lead if component is specified'

    for component in payload['components']:
      component_lead = toolbox.return_component_lead(component, payload['project_name'])
      if component_lead:
        print 'Assigning bug issue to:'
        print payload['issue_key'], 'Component:',component,'lead to assign is:', component_lead
        issue = jira.issue(payload['issue_key'])
        jira.assign_issue(issue, component_lead)
        return True