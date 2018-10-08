# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA
import team_members

def force_to_unicode(text):
  if text:
      #"If text is unicode, it is returned as is. If it's str, convert it to Unicode using UTF-8 encoding"
      return text if isinstance(text, unicode) else text.decode('utf8')

def set_source_by_owner(payload, jira):
  #this function will run through the teams structure and
  #will set the owner by the reporter field
  #configure jira issue object
  #in this example the custom field 10900 is 'SOURCE' indicating where the issue was originated from
  jirauser = str(os.environ.get('JIRAUSER'))

  if payload['reporter'] != jirauser and (payload['source'] == 'Not set' or payload['source'] == 'Unknown' or payload['source'] == 'None'):
    issue = jira.issue(payload['issue_key'])  
    transitions = jira.transitions(issue)

    #invoke the teams structure module
    org_teams = team_members.load_team_members()

    #if the new issue was reported by a member of A team set the source of it to team
    #team structure is provided from cloudinary team module
    for team in org_teams:
      if any(member in payload['reporter'] for member in cld_team[team]) and payload['source'] != team:
        print "Since the issue was reported by a member of the:", team, "team, will set the source as", team
        issue.update(fields={'customfield_10900': {'value': team }}) #set "source" to the dictionary key

def check_for_linked_doc(key, jira):
  issue = jira.issue(key)
  doc_issues = []
  try:
    for x in issue.raw['fields']['issuelinks']:
      key = str(x['outwardIssue']['key'])
      kind = str(x['type']['inward'])
      if 'DOC' in key and 'caused' in kind:
        #if a doc issues is found append it to the list
        doc_issues.append(key)
    if len(doc_issues) == 0:
      return False
    else:
      print 'Found the following linked doc issues:', doc_issues
      return doc_issues
  except Exception as e:
    return False

def open_linked_issue(payload, jira):
  #this function will verify that an issue with the requirment for a doc issue 
  #has a valid doc issue with a link to it
  #list of project codes we act upon
  #in new_issue_dict a project key must be set and a prefix may be added
  
  issue = jira.issue(payload['issue_key']) 

  if condition == 'met':
    #first check we dont have a linked issue to avoid duplications
    if check_for_linked_doc(payload['issue_key'], jira) is False:
      print payload['issue_key'], " Requires marked as Update required but already has linked DOC issue"
    else:
      new_issue_dict = {'project': {'key': 'XXX'},
                        'summary': "prefix: " + payload['jira_summary'] ,
                        'description': payload['jira_description'] ,
                        'issuetype': {'name' : 'Story'},
                        'priority' : {'name' : payload['jira_priority']}
                        }

      print "will open a new issue with following parameters:"
      print (json.dumps(new_issue_dict, sort_keys=True))
      
      new_issue = jira.create_issue(fields=new_issue_dict)
      print "New jira issue created:", new_issue.key
      
      print "Will now assign ", new_issue.key ," to a team"
      jira.assign_issue(new_issue, 'team')
      
      print "Will now set source team according to the causing jira"
      new_issue.update(fields={'customfield_10900': {'value': payload['source'] }}) #set "source" to the dictionary key

      if payload['epic'] == 'Not set':
        print "Since Parent had no epic, i wont set one"
      else:
        print "Will set new issue with causing's epic key:"
        new_issue.update(fields={'customfield_10004': {'value': payload['epic'] }})

      #linking the issue as the last action to make sure the doc team isnt spammed with the clutter from all actions
      print "Will now link:", issue.key, "to:", new_issue.key
      jira.create_issue_link(type='Problem/Incident', inwardIssue=issue.key, outwardIssue=new_issue.key)

def enforce_field_on_issue(payload, jira):
  #this issue can be used to enforce a certail policy on a specific type of issues
  issue = jira.issue(payload['issue_key'])
  #if new issue contains component as one of the components set the qa required to yes  
  if "component" in payload['components']:
    print "Since jira issue components contains component make sure somthing is enforced on:", payload['issue_key']
    issue.update(fields={'customfield_XXXX': {'value': 'Yes'}}) #set "requires qa" to Yes
