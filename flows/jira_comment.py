# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA
from rq import Queue
from worker_all_priority import conn

import jira_generate_payload
import jira_issue_toolbox
import team_members
import notify_mentioned_by_slack
import notify_cs_of_zendesk_issue
import jira_connector as j

def new_comment_flow(request_json_payload, jira=j.setup_jira_object()):
	data = json.loads(request_json_payload)
	# print (json.dumps(data, sort_keys=True))

	jira_key = data['issue']['key']
	q = Queue(connection=conn)

	#notify users apprearing on activating comment hook
	q.enqueue(notify_mentioned_by_slack.notify_mentioned_users_in_comment, data['comment']['body'], jira_key)

	return "200"
