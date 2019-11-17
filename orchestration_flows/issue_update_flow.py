# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA
from rq import Queue
from worker_all_priority import conn

import jira_generate_payload
import jira_issue_toolbox as toolbox
import team_members
import doc_issue_auto_creation
import notify_mentioned_by_slack
import notify_cs_of_zendesk_issue

def updated_issue_hook(request_json_payload, jira, triggering_user):
  data = json.loads(request_json_payload)
  payload = jira_generate_payload.generate_payload(data)


  jira_key = payload['issue_key'].encode('utf-8')
  q = Queue(connection=conn)

  #make sure that when qa opens a bug the manual qa field is set correctly
  q.enqueue(toolbox.enforce_qa_when_qa_team, jira_key, result_ttl=0)

  #make bugs with priority ready for dev
  q.enqueue(toolbox.set_bugs_with_priority_as_ready, jira_key, result_ttl=0)

  #done issues with fixed version set are set as Deployed
  q.enqueue(toolbox.set_done_issues_with_fixversion_as_deployed, jira_key, result_ttl=0)

  #verify doc issue linkage
  q.enqueue(doc_issue_auto_creation.link_to_doc_issue, jira_key, result_ttl=0)
  
  #notify CS of completed zendesk issues - plug issues created by them
  q.enqueue(notify_cs_of_zendesk_issue.manage_cs_notifications, payload['reporter_email'], jira_key, result_ttl=0)

  #Once flow is done, it ok to return 200    
  return "200"

  if __name__=='__main__':
    issue_update_hook()