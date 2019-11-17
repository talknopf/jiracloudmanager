# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA
from rq import Queue
from worker_all_priority import conn

#cloudinary toolbox modules
import jira_generate_payload
import jira_issue_toolbox as toolbox
import addon_flow
import new_projects_addon_flow
import doc_issue_auto_creation
import set_bug_owner_by_component_lead
import assign_epic_to_reporter

def new_issue_hook(request_json_payload, jira):
  data = json.loads(request_json_payload)
  payload = jira_generate_payload.generate_payload(data)
  
  jira_key = payload['issue_key'].encode('utf-8')
  #connect to worker que
  q = Queue(connection=conn)

  #make sure that when qa opens a bug the manual qa field is set correctly
  q.enqueue(toolbox.enforce_qa_when_qa_team, jira_key, result_ttl=0)

  #make sure new issues reported by rnd and assigned to rnd are set as ready for dev.
  q.enqueue(toolbox.rnd_to_rnd_set_ready_for_dev, jira_key, result_ttl=0)
  
  #addon story creation automation
  q.enqueue(new_projects_addon_flow.detect_if_issue_needs_automation, jira_key, result_ttl=0)

  #verify doc issue linkage
  q.enqueue(doc_issue_auto_creation.link_to_doc_issue, jira_key, result_ttl=0)

  #addon assign to project lead automation
  q.enqueue(product_lead_auto_assign.product_lead_auto_assign, jira_key, result_ttl=0)
  
  #addon to assign bug assignee by component owner
  q.enqueue(set_bug_owner_by_component_lead.bug_set_assignees_component_lead, jira_key, result_ttl=0)

  #when creating new Epic issue if un-assigned assign to creator
  q.enqueue(assign_epic_to_reporter.unassigned_epic_auto_assign, jira_key, result_ttl=0)

  #when logic flow is done, return 200
  return "200"

if __name__=='__main__':
	new_issue_hook()