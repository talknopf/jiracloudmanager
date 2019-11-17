import os
import sys
import json
from jira import JIRA
from flask import Flask, request
import re

import github_generate_pr_payload
import generate_payload_by_id
import jira_issue_toolbox as toolbox
import jira_connector as j

def github_main(request,jira):
  '''
  if a PR is merged then try and find the related jira for it.
  If developer merges in GITHUB to MASTER (from branch) and jira issue status is In Review -
  check the field Manual Testing and transition issue status accordingly:
  when  = 'Not Applicable', change status to Merged-Tested
  when  = 'On Testing Env', change status to Merged-Tested
  when  field is not set, change status to Merged-Tested
  when  = 'on master', change status to Merge-Test On Master
  when  = 'On Production', change status to Merged-Not Tested
  When  = "On Branch", change status to Test On Branch
  '''

  gh_payload = github_generate_pr_payload.generate_payload(request, jira)
  if gh_payload['action'] == 'closed' and gh_payload['merged']:
    print "going to search for a linked issue in jira and if exist will transition to the desired status"
    if gh_payload['linked_jira_issue']:
      print "found a linked jira issue: " + str(gh_payload['linked_jira_issue'])
      payload = generate_payload_by_id.generate_payload(gh_payload['linked_jira_issue'])
      if payload['project_name'] in ['APPS', 'CORE'] and payload['status'].lower() == 'in review':
        transition_issue_based_on_manual_qa_field(gh_payload, payload)
      else:
        print "github event is not a relevant flow since linked jira issue project name: " + str(payload['project_name']) + ", jira issue status: " + str(payload['status'])
    else:
      print "github event is not a relevant flow since there isn't any linked jira issue related to the github branch"
  else:
    print "github event is not a relevant flow since action: " + str(gh_payload['action']) + ", merge: " + str(gh_payload['merged'])

  #overflow if nothing is done
  return "200"


def transition_issue_based_on_manual_qa_field(github_event_payload, jira_issue_payload):
  print "going to transition issue based on manual_qa field"

  linked_issue_jira_key = github_event_payload['linked_jira_issue']
  linked_issue_manual_qa_field = jira_issue_payload['manual_qa']
  pr_url = github_event_payload['pull_request_html_url']

  if linked_issue_manual_qa_field.lower() in ['Option1', 'Option2', 'Option3']:
    transition_and_comment('Merge - Tested', pr_url, linked_issue_jira_key)

  else:
    print "manual qa field value is: " + str(jira_issue_payload['manual_qa']) + " and don't have a relevant transition"


def transition_and_comment(desired_status, pr_url, jira_key, jira=j.setup_jira_object()):
  res = toolbox.transition_to_status(jira_key=jira_key, desired_status=desired_status)
  if res:
    print "Transition completed on issue: " + str(jira_key)
    comment_text = 'Status was transitioned by Yentel since PR was merged and referenced: ' + str(pr_url)
    print "adding comment to jira issue : " + str(comment_text)
    jira.add_comment(jira_key, comment_text)
