# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA
from rq import Queue
from worker_all_priority import conn

# cloudinary toolbox modules
import jira_generate_payload
import jira_issue_toolbox as toolbox


def doc_update_issue(request_json_payload, jira):
    data = json.loads(request_json_payload)
    payload = jira_generate_payload.generate_payload(data)

    jira_key = payload['issue_key'].encode('utf-8')
    # connect to worker que
    q = Queue(connection=conn)

    # make sure the new media lib. issues are passed on to QA
    q.enqueue(toolbox.update_doc_trigger_status, jira_key, result_ttl=0)

    return "200"
