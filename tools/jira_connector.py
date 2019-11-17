# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA

def setup_jira_object():
  jirauser = str(os.environ.get('JIRAUSER'))
  jirapass = str(os.environ.get('JIRAKEY'))
  jiraserver = str(os.environ.get('JIRASERVER'))
  jira = JIRA(basic_auth=(jirauser, jirapass), options={'server': jiraserver})
  return jira