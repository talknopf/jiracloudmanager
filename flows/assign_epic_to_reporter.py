# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA

sys.path.append('../tools/')

import jira_issue_toolbox as toolbox
import generate_payload_by_id
import jira_connector as j

def unassigned_epic_auto_assign(jira_key, jira=j.setup_jira_object()):
  projects_to_check = ['CLD' ,'SDK']
  payload = generate_payload_by_id.generate_payload(jira_key)
  
  #set issue object since we will need it
  issue = jira.issue(payload['issue_key'])

  if toolbox.issue_is_epic(payload) and not toolbox.issue_is_assigned(payload):
  	print payload['issue_key'], 'Since issues is Epic and is un-assigned will assign to reporter:', payload['reporter']
  	jira.assign_issue(issue, payload['reporter'])
