# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA

sys.path.append('../tools/')

import jira_issue_toolbox as toolbox
import generate_payload_by_id
import jira_connector as j

def component_lead_auto_assign(jira_key, jira=j.setup_jira_object()):
  projects_to_check = ['CLD' ,'SDK']
  payload = generate_payload_by_id.generate_payload(jira_key)
  
  #set issue object since we will need it
  issue = jira.issue(payload['issue_key'])

  if toolbox.issue_is_security_event(payload):
    #handle case of security issue without component set component to Security
    if len(payload['components']) == 0:
      issue.update(fields={"components": [{ 'name' : 'Security' }]})
      payload = generate_payload_by_id.generate_payload(jira_key)
      
    for component in payload['components']:
      component_lead = toolbox.return_component_lead(component, payload['project_name'])
      if component_lead:
        print payload['issue_key'], 'Will assign issue to product lead:', component_lead
        issue = jira.issue(payload['issue_key'])
        jira.assign_issue(issue, component_lead)
        return True