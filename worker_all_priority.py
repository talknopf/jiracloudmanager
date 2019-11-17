# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA
import redis
from rq import Worker, Queue, Connection

#python path allocation
sys.path.append('flows/')
sys.path.append('tools/')

#tools modules
import cloudinary_teams
import yentel_slack as slack
import jira_issue_toolbox as toolbox
import generate_payload_by_id

#cloudinary flows
import doc_issue_auto_creation
import notify_cs_of_zendesk_issue
import set_bug_owner_by_component_lead
import assign_epic_to_reporter
import jira_connector as j

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()