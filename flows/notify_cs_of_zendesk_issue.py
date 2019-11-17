# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA

sys.path.append('../tools/')

import jira_issue_toolbox as toolbox
import generate_payload_by_id
import yentel_slack as slack
import jira_connector as j

def should_report(payload, projects_to_check, desired_statuss):
	if toolbox.issue_within_projects(payload, projects_to_check) and toolbox.is_member_of_team(payload['reporter'], 'CS') and payload['status'] in desired_statuss:
		if 'notified_cs_by_slack' not in payload['labels']:
			print payload['issue_key']+' Since issue was reported by cs will notify them by slack'
			return True
	elif toolbox.issue_within_projects(payload, projects_to_check) and payload['reporter'] == 'addon_zendesk_for_jira' and payload['status'] in desired_statuss:
		if 'notified_cs_by_slack' not in payload['labels']:
			print payload['issue_key']+' Since issue was reported by addon_zendesk_for_jira will notify cs by slack'
			return True
	else:
		return False

def report_to_cs_by_slack(payload, jira=j.setup_jira_object()):

	reporter_user_id = slack.convert_email_to_slack_id(payload['reporter_email'])

	text_line = "Head's up! an issue <@"+str(reporter_user_id)+"> worked on was just marked as " + payload['status']

	message_for_channel = [{
		"fallback": "",
		"pretext": "A Jira Issue Created By CS Was Just Closed",
		"title": payload['issue_key']+": "+payload['jira_summary'],
		"title_link": 'https://cloudinary.atlassian.net/browse/'+payload['issue_key'],
		"text": text_line,
		"color": "#7CD197"
	}]
	slack.message_to_channel('', 'cs-jira-updates',message_for_channel)
	payload['labels'].append('notified_cs_by_slack')
	issue = jira.issue(payload['issue_key'])
	issue.update(notify=False, fields={"labels": payload['labels']})
def notify_cs_team_of_resolved_sdk_issue(payload, jira):
	if should_report(payload,['SDK'], ['Published']):
		report_to_cs_by_slack(payload)
      
def notify_cs_team_of_deployed_cld_and_prod_issue(payload, jira):
	if should_report(payload, ['CLD','PROD','APPS','CORE'],['Deployed','Done']):
		report_to_cs_by_slack(payload)

def notify_cs_team_of_sol_issue(payload, jira):
	if should_report(payload,['SOL'],['Done']):
		report_to_cs_by_slack(payload)

def notify_cs_team_of_doc_issue(payload, jira):
	if should_report(payload,['DOC'], ['Done']):
		report_to_cs_by_slack(payload)

def manage_cs_notifications(reporter_email ,jira_key, jira=j.setup_jira_object()):
	payload = generate_payload_by_id.generate_payload(jira_key)
	payload["reporter_email"] = reporter_email

 	notify_cs_team_of_resolved_sdk_issue(payload, jira)
	notify_cs_team_of_deployed_cld_and_prod_issue(payload, jira)
	notify_cs_team_of_sol_issue(payload, jira)
	notify_cs_team_of_doc_issue(payload, jira)