# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA

sys.path.append('../tools/')

import jira_issue_toolbox as toolbox
import generate_payload_by_id
import jira_connector as j

#Logic and decision making
def detect_if_issue_needs_automation(jira_key, jira=j.setup_jira_object()):
	payload = generate_payload_by_id.generate_payload(jira_key)
	print jira_key, " checking if issue is product epic (add-on) in need of subtask creation"
	if toolbox.issue_is_epic(payload) and has_addon_in_jira_summary(payload):
		addon_name = detect_addon_name_from_jira_summary(payload)
		print addon_name
		generate_doc_tasks(payload, jira, addon_name)
		# generate_sdk_tasks(payload, jira, addon_name)
		generate_be_tasks(payload, jira, addon_name)
		generate_fe_tasks(payload, jira, addon_name)
		generate_design_tasks(payload, jira, addon_name)
		generate_product_tasks(payload, jira, addon_name)

def detect_addon_name_from_jira_summary(payload):
	summary_parts = str(payload['jira_summary']).lower().split(':')
	addon_parts = ['add', 'on', 'addon','add-on']
	for i in addon_parts:
		if i in summary_parts[0]:
			return str(summary_parts[1]).lower().lstrip()

def has_addon_in_jira_summary(payload):
	if detect_addon_name_from_jira_summary(payload):
		return True

#,'APPS','CORE'
#Actuall creation tasks
def generate_be_tasks(payload, jira, addon_name):
	#generate tasks for specs Implement add-on "X".
	new_issue_dict_list = [{'project': {'key': 'CORE'},
	                        'summary': "Implement add-on: " + addon_name ,
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        },
	                        {'project': {'key': 'CORE'},
	                        'summary': "Add " + payload['summary'] + " add-on to \'allow unsigned\' Security setting" ,
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        }]

	for new_issue_dict in new_issue_dict_list:
		print "will open a new CLD issue with following parameters:"
		print (json.dumps(new_issue_dict, sort_keys=True))

		new_issue = jira.create_issue(fields=new_issue_dict)
		print "New jira issue created:", new_issue.key

		print "Will now assign ", new_issue.key ," to R&D team"
		jira.assign_issue(new_issue, 'R&D')

def generate_fe_tasks(payload, jira, addon_name):
	#fe tasks and sdk to corrolate
	new_issue_dict_list = [{'project': {'key': 'APPS'},
	                        'summary': "Create add-on snippet for: " + payload['summary'] ,
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        },
	                        {'project': {'key': 'APPS'},
	                        'summary': "Add " + payload['summary'] + " add-on to Upload Preset UI" ,
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        }]
	for new_issue_dict in new_issue_dict_list:
		print "will open a new CLD issue with following parameters:"
		print (json.dumps(new_issue_dict, sort_keys=True))

		new_issue = jira.create_issue(fields=new_issue_dict)
		print "New jira issue created:", new_issue.key

		print "Will now assign ", new_issue.key ," to R&D team"
		jira.assign_issue(new_issue, 'cloudinarydam')

def generate_sdk_tasks(payload, jira, addon_name):
	#generate sdk tasks
	#documentaions and blog posts
	sdk_langs = ['java script','java','php','ruby','iOS','.Net','jquery','django','scala','node .js','angular','wordpress','php','android','marketo']
	# sdk_langs = ['java']
	new_issue_dict_list = []
	for lang in sdk_langs:
		new_issue_dict_template = {'project': {'key': 'SDK'},
		                        'summary': "Support add-on: " + addon_name + " In:" + lang ,
		                        'description': payload['jira_description'] ,
		                        'issuetype': {'name' : 'Story'},
		                        'priority' : {'name' : 'Medium'},
		                        'components' : payload['parsed_components'],
		                        'customfield_10900': {'value': 'Product' },
		                        'customfield_10004': payload['issue_key']
		                        }
    	new_issue_dict_list.append(new_issue_dict_template)

	for new_issue_dict in new_issue_dict_list:
		print "will open a new DOC issue with following parameters:"
		print (json.dumps(new_issue_dict, sort_keys=True))

		new_issue = jira.create_issue(fields=new_issue_dict)
		print "New jira issue created:", new_issue.key

		print "Will now assign ", new_issue.key ," to SDK team"
		jira.assign_issue(new_issue, 'cloudinarysdk')

def generate_design_tasks(payload, jira, addon_name):
	#Design tasks for product
	new_issue_dict_list = [{'project': {'key': 'APPS'},
	                        'summary': "Create add-on icon for : " + payload['summary'] ,
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        },
	                        {'project': {'key': 'APPS'},
	                        'summary': "Create graphics for add-on snippet: " + payload['summary'],
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        },
	                        {'project': {'key': 'APPS'},
	                        'summary': "Apply add-on plan for " + payload['summary'],
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        }]
	for new_issue_dict in new_issue_dict_list:
		print "will open a new CLD issue with following parameters:"
		print (json.dumps(new_issue_dict, sort_keys=True))

		new_issue = jira.create_issue(fields=new_issue_dict)
		print "New jira issue created:", new_issue.key

		print "Will now assign ", new_issue.key ," to Boaz"
		jira.assign_issue(new_issue, 'boaz')

def generate_doc_tasks(payload, jira, addon_name):
	#documentaions and blog posts
	new_issue_dict_list = [{'project': {'key': 'DOC'},
	                        'summary': "Document add-on: " + addon_name ,
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        },
	                        {'project': {'key': 'DOC'},
	                        'summary': "add-on snippet text for: " + payload['summary'] ,
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        }
    ]
	for new_issue_dict in new_issue_dict_list:
		print "will open a new DOC issue with following parameters:"
		print (json.dumps(new_issue_dict, sort_keys=True))

		new_issue = jira.create_issue(fields=new_issue_dict)
		print "New jira issue created:", new_issue.key

		print "Will now assign ", new_issue.key ," to Docs team"
		jira.assign_issue(new_issue, 'docs')

def generate_product_tasks(payload, jira, addon_name):
	#Design tasks for product
	new_issue_dict_list = [{'project': {'key': 'APPS'},
	                        'summary': "Apply add-on plan for " + payload['summary'],
	                        'description': payload['jira_description'] ,
	                        'issuetype': {'name' : 'Story'},
	                        'priority' : {'name' : 'Medium'},
	                        'components' : payload['parsed_components'],
	                        'customfield_10900': {'value': 'Product' },
	                        'customfield_10004': payload['issue_key']
	                        }]
	for new_issue_dict in new_issue_dict_list:
		print "will open a new CLD issue with following parameters:"
		print (json.dumps(new_issue_dict, sort_keys=True))

		new_issue = jira.create_issue(fields=new_issue_dict)
		print "New jira issue created:", new_issue.key

		print "Will now assign ", new_issue.key ," to Product"
		jira.assign_issue(new_issue, 'product')
