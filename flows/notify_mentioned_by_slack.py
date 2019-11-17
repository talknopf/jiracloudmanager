import os
import sys
import json
import re
from jira import JIRA
import jira_issue_toolbox as toolbox
import yentel_slack as slack
import jira_connector as j

def notify_mentioned_users_in_comment(comment_body, jira_id, jira=j.setup_jira_object()):
	issue = jira.issue(jira_id)
	mentioned_users = []
	if '~' in comment_body:
		comment_parts = toolbox.force_to_unicode(comment_body).split(' ')
		for word in comment_parts:
			if '~' in word:
				this_user = re.sub('(.*\s*\[~)([a-z]+\.*[a-z]*)(\]\s*.*\n*)', r'\2@cloudinary.com', word)
				# print "word - ", word
				# print "this user", this_user
				# this_user = this_user.encode('utf-8')
				if this_user not in mentioned_users:
					this_user = toolbox.force_to_unicode(str(this_user))
					print issue.key , " - Found mentioning of: ", this_user ," in added comment"
					mentioned_users.append(this_user)

	if len(mentioned_users)>0:
		for user in mentioned_users:
			print issue.key, "notifying:", user
			ms = [{
				"fallback": "",
				"pretext": "You were just mentioned in an "+issue.fields.project.key+" Jira issue",
				"title": str(issue.key)+": "+str(issue.fields.summary),
				"title_link": 'https://cloudinary.atlassian.net/browse/'+str(issue.key),
				"text": "Head's up! somone just mentioned you on Jira\n"+comment_body+"\n *To reply to this comment please click the link to login to jira*",
				"color": "#7CD197"
	      	}]

	      	slack.message_to_user(user, ms)

def find_mentioned_commentees(jira_id, jira=j.setup_jira_object()):
	issue = jira.issue(jira_id)
	mentioned_users = []
	if issue.fields.comment.comments:
		last_comment_text = issue.fields.comment.comments[-1].body.encode('utf-8')
		if '~' in last_comment_text:
			last_comment_parts = toolbox.force_to_unicode(str(last_comment_text)).split(' ')
			for word in last_comment_parts:
				if '~' in word:
					this_user = re.sub('(.*\s*\[~)([a-z]+\.*[a-z]*)(\]\s*.*\n*)', r'\2@cloudinary.com', word)
					this_user = this_user.encode('utf-8')
					if this_user not in mentioned_users:
						this_user = toolbox.force_to_unicode(str(this_user))
						print issue.key , " - Found mentioning of: ", this_user 
						mentioned_users.append(this_user)
	return mentioned_users

def notify_mentioned_users(jira_id, jira=j.setup_jira_object()):
	issue = jira.issue(jira_id)
	mentioned_users = find_mentioned_commentees(issue.key)
	if len(mentioned_users)>0:
		for user in mentioned_users:
			print issue.key, "notifying:", user
			last_comment_text = issue.fields.comment.comments[-1].body.encode('utf-8')
			last_comment_text = toolbox.force_to_unicode(str(last_comment_text))
			ms = [{
				"fallback": "",
				"pretext": "You were just mentioned in an "+issue.fields.project.key+" Jira issue",
				"title": str(issue.key)+": "+str(issue.fields.summary),
				"title_link": 'https://cloudinary.atlassian.net/browse/'+str(issue.key),
				"text": "Head's up! somone just mentioned you on Jira\n"+last_comment_text+"\n *To reply to this comment please click the link to login to jira*",
				"color": "#7CD197"
	      	}]

	      	slack.message_to_user(user, ms)