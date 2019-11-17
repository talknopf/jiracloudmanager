# -*- coding: utf-8 -*-
import os
import sys
import json
from slackclient import SlackClient
import jira_issue_toolbox as toolbox

slack_token = os.environ.get("SLACK_TOKEN")

sc = SlackClient(slack_token)

def convert_email_to_slack_id(jira_email):
	jira_email = toolbox.force_to_unicode(jira_email)
	while not jira_email[0].isalpha(): jira_email = jira_email[1:]
	slack_payload = sc.api_call("users.lookupByEmail", email=jira_email)
	if slack_payload['ok'] is True:
		return slack_payload['user']['id']

def message_to_user(target_user_email, rich_message):
	if target_user_email == 'nobody@your-org-here.com':
		return False #if no valid e-mail is supplied the function will quit here
	user_slack_id = convert_email_to_slack_id(target_user_email)
	if user_slack_id:
		print target_user_email +" Has slack id: "+user_slack_id
		sc.api_call( 
			"chat.postMessage",
			channel=user_slack_id,
			attachments=rich_message
		)
	else:
		print "Unable to fetch user ID so will try to notify by email"
		chopped_email = str(target_user_email.split('.')[0])+'@your-org-here.com'
		user_slack_id = convert_email_to_slack_id(chopped_email)
		print "user_slack_id:", user_slack_id
		print "user_email:", target_user_email
		print "chopped_email", chopped_email
		sc.api_call( 
			"chat.postMessage",
			channel=target_user_email,
			attachments=rich_message
		)
	


def message_to_channel(message_text, target_channel, rich_message):
	message_text = toolbox.force_to_unicode(message_text)
	if rich_message:
		sc.api_call( 
			"chat.postMessage",
			channel=target_channel,
			attachments=rich_message
		)
	else:
		sc.api_call( 
			"chat.postMessage",
			channel=target_channel,
			text=message_text,
		)
