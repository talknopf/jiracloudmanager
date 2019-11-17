# -*- coding: utf-8 -*-
import os
import sys
import json
from jira import JIRA
from flask import request
import cloudinary_teams
import yentel_slack as slack
import jira_generate_payload
import generate_payload_by_id
import jira_connector as j

def should_exclude_request(request):
  username = request.args.get('user_id')
  if username == 'cloudinaryentel' or username == 'addon_zendesk_for_jira':
    print 'Since update was triggered from', username,', I will be ignore it'
    return True

def force_to_unicode(text):
  try:
    return str(text)
  except UnicodeEncodeError:
    return text.encode('ascii', 'ignore').decode('ascii')
  return ""

def set_source_by_owner(jira_key, jira=j.setup_jira_object()):
  #this function will run through the cloudinary team structure and
  #will set the owner by the reporter field
  #configure jira issue object
  payload = generate_payload_by_id.generate_payload(jira_key)
  def issue_source_not_defined(payload):
    return (payload['source'] == 'Not set' or payload['source'] == 'Unknown' or payload['source'] == 'None')    
  
  if not reported_by_yentel(payload) and issue_source_not_defined(payload):
    issue = jira.issue(payload['issue_key'])

    #invoke the teams structure module
    cld_team = cloudinary_teams.load_team_members()

    for team in cld_team:
      if is_member_of_team(payload['reporter'], team) and payload['source'] != team:
        print "Since the issue was reported by a member of the:", team, "team, will set the source as", team
        issue.update(fields={'customfield_10900': {'value': team }}) #set "source" to the dictionary key


def reported_by_yentel(payload):
  return payload['reporter'] == 'yentel'

def is_member_of_team(checked_user, team_name):
  #invoke the teams structure module
  cld_team = cloudinary_teams.load_team_members()
  for memeber in cld_team[team_name]:
    if memeber == checked_user:
      return True
  #if logic got so far, then the checked user is not a memeber
  return False

def is_not_member_of_team(checked_user, team_name):
  return not is_member_of_team(checked_user, team_name)

#will look for a secific code related issue in target jira
def check_for_linked_issue_by_project(key, jira, project):
  issue = jira.issue(key)
  linked_issues = []
  project_key = str(project)
  linked_obj = issue.raw['fields']['issuelinks']
  print 'Checking for linked ' + project_key + 's in:'+ key
  for x in linked_obj:
    if 'outwardIssue' in x:
      key = x['outwardIssue']['key']
      kind = x['type']['inward']
      if project_key in key and kind == 'is caused by':
        #if a doc issues is found append it to the list
        linked_issues.append(key)
  if len(linked_issues) == 0:
    print 'Could not find any ' + project_key + 's in:'+ key
    return False
  else:
    print 'Found the following linked issues:', linked_issues
    return linked_issues

def check_for_related_issues(key, jira=j.setup_jira_object()):
  issue = jira.issue(key)
  linked_issues = []
  linked_obj = issue.raw
  print 'Checking for related issues in ' + key
  for x in linked_obj['fields']['issuelinks']:
    if 'outwardIssue' in x:
      if x['type']['inward'] == 'relates to':
        linked_issues.append(x['outwardIssue']['key'])
    elif 'inwardIssue' in x and linked_obj['fields']['issuetype']['name'] == 'Epic':
      if x['type']['inward'] == 'relates to':
        linked_issues.append(x['inwardIssue']['key'])
            
  if len(linked_issues) == 0:
    print 'Could not find any related issues in: ' + key
    return False
  else:
    print 'Found the following related issues:', linked_issues
    return linked_issues


def transition_linked_issues(linked_issues, desired_state, jira=j.setup_jira_object()):
  for linked_issue in linked_issues:
    linked_issue_obj = jira.issue(linked_issue)
    linked_issue_status = linked_issue_obj.raw['fields']['status']['name']
    print 'Checking linked issue:', str(linked_issue) , 'the status of it is:', linked_issue_status
    if linked_issue_status != 'Done':
      transition_to_status(linked_issue, desired_state, jira)

def mark_related_undone_tasks_with_warning_comment(jira_key, jira=j.setup_jira_object()):
  payload = generate_payload_by_id.generate_payload(jira_key)
  if is_status_done(payload):
    related_issues_list = check_for_related_issues(payload['issue_key'], jira)
    if related_issues_list:
      for related_issue in related_issues_list:
        print "checking status of related issue: " + str(related_issue)
        if not is_issue_key_done(related_issue, jira):
          print "Since " + str(related_issue) + " is not done will add a release note remarking this issue"
          un_done_issue = jira.issue(related_issue)
          new_release_notes = "an issue related to this was marked as done, so adding release notes for notice \n" + payload['release_notes']
          un_done_issue.update(fields={'customfield_11000': new_release_notes})

def enforce_qa_when_qa_team(jira_key, jira=j.setup_jira_object()):
  payload = generate_payload_by_id.generate_payload(jira_key)
  if is_member_of_team(payload['reporter'], 'QA') and not requires_qa(payload) and issue_is_bug(payload):
    enforce_qa_on_issue(jira_key, 'On Master')

def enforce_qa_on_issue(jira_key, desired_state, jira=j.setup_jira_object()):
  print "Enforcing QA on issue:", jira_key
  set_manual_qa_to(desired_state, jira_key, jira)

def is_status_merged(payload):
  return payload['status'] in ['Merged-Not Tested','Merged-Tested']

def is_status_done(payload):
  return payload['status'] == 'Done'

def is_status_deployed(payload):
  return payload['status'] == 'Deployed'

def is_status_published(payload):
  if payload['project_name'] == 'SDK':
    return payload['status'] == 'Published'
  else:
    return False
    
def issue_has_epic(payload):
  if payload['epic'] and isinstance(payload['epic'], basestring):
    return True

def is_issue_key_done(issue_key, jira=j.setup_jira_object()):
  issue = jira.issue(issue_key)
  issue_status = issue.raw['fields']['status']['name']
  return issue_status == 'Done'

def issue_has_priority(payload):
  return (payload['jira_priority'] != 'None')

def issue_is_bug(payload):
  return (payload['issuetype'] == 'Bug')

def issue_is_task(payload):
  return (payload['issuetype'] == 'Task')

def issue_is_story(payload):
  return (payload['issuetype'] == 'Story')

def issue_is_security_event(payload):
  return (payload['issuetype'] == 'Security Event')

def issue_is_epic(payload):
  return (payload['issuetype'] == 'Epic')

def requires_qa(payload):
  if payload['qa_required'] or payload['manual_qa']:
    if payload['manual_qa'] in ['On Testing Env','On Production'] or payload['qa_required']=='Yes':
      return True
  else:
    return False

def requires_documentation(payload):
  if payload['docs_impact'] or payload['documentation']:
    if payload['documentation'] == 'Required' or payload['docs_impact'] == 'Update required':
      return True
  else:
    return False

def required_sdk(payload):
  if payload['sdk_impact'] or payload['sdk_link']:
    if payload['sdk_impact'] == 'Yes' or payload['sdk_link'] == 'Required':
      return True
  else:
    return False

def issue_is_assigned(payload):
  return payload['assignee'] != 'Nobody'

def set_manual_qa_to(selection, issue_key, jira=j.setup_jira_object()):
  issue = jira.issue(issue_key)
  issue.update(fields={'customfield_12042': {'value': selection}})

def transition_to_status(jira_key, desired_status, jira=j.setup_jira_object()):
  print "will try to transition " + jira_key + " to status:" + desired_status
  target_issue = jira.issue(jira_key)
  transitions = jira.transitions(target_issue)
  for t in transitions:
    if desired_status.lower().strip() in t['name'].lower().strip():
      jira.transition_issue(target_issue, t['id'])
      return True
  return False

def set_bugs_with_priority_as_ready(jira_key, jira=j.setup_jira_object()):
  projects_to_check = ['CLD','PROD','APPS','CORE']
  payload = generate_payload_by_id.generate_payload(jira_key)
  if issue_within_projects(payload, projects_to_check):
    if issue_is_bug(payload) and issue_has_priority(payload) and payload['status'] == 'To do':
      transition_to_status(payload['issue_key'], 'Ready for dev', jira)

def issue_within_projects(payload, projects_to_check):
  return payload['project_name'] in projects_to_check

def set_done_issues_with_fixversion_as_deployed(jira_key, jira=j.setup_jira_object()):
  #list of project codes we act upon
  projects_to_check_new = ['APPS','CORE']
  payload = generate_payload_by_id.generate_payload(jira_key)
  if is_status_merged(payload) and issue_within_projects(payload, projects_to_check_new):
    for fv in payload['fixversion']:
      if 'deployed' in str(fv):
        print "Issue has fix version and status is done, so converting to deployed state"
        transition_to_status(payload['issue_key'], 'Deployed', jira)
 
  projects_to_check_old = ['SDK' ,'CLD' ,'PROD']
  if is_status_done(payload) and issue_within_projects(payload, projects_to_check_old):
    for fv in payload['fixversion']:
      if 'deployed' in str(fv):
        print "Issue has fix version and status is done, so converting to deployed state"
        transition_to_status(payload['issue_key'], 'Deployed', jira)

def rnd_to_rnd_set_ready_for_dev(jira_key, jira=j.setup_jira_object()):
  projects_to_check = ['CLD','PROD','APPS','CORE']
  payload = generate_payload_by_id.generate_payload(jira_key)
  if issue_within_projects(payload, projects_to_check):
    if is_member_of_team(payload['assignee'], 'R&D') and is_member_of_team(payload['reporter'], 'R&D'):
      if payload['status'] == 'To Do':
        print payload['issue_key'] ,"since the reporter is from rnd team and the issue is assigned to rnd with status todo will change to Ready for dev"
        transition_to_status(payload['issue_key'], 'Ready for dev', jira)

def doc_team_memeber_to_memeber(payload, jira=j.setup_jira_object()):
  #if an issue is opned by doc team member set it as ready for dev
  if is_member_of_team(payload['assignee'], 'Documentation') and is_member_of_team(payload['reporter'], 'Documentation'):
    if payload['status'] == 'To Do':
      print "Issue: ", payload['issue_key'] , "Was created by member of the doc team, and is assined to a memeber of the doc team, so will transition to ready for dev"
      transition_to_status(payload['issue_key'], 'Ready for dev', jira)
def convert_components_to_set(components_list):
  list_of_sets=[]
  for i in components_list:
    item = {'name': i }
    list_of_sets.append(item)
  return list_of_sets

def add_label_to_issue(jira_key, label_to_add, jira=j.setup_jira_object()):
  issue = jira.issue(jira_key)
  print 'Adding label:'+label_to_add+' to issue: '+ jira_key +' if its not there'
  current_labels = issue.fields.labels
  if label_to_add not in current_labels:
    current_labels.append(label_to_add)
    issue.update(fields={'labels': current_labels})

def remove_label_from_issue(jira_key, label_to_remove, jira=j.setup_jira_object()):
  issue = jira.issue(jira_key)
  print 'Removing label:'+label_to_remove+' to issue: '+ jira_key +' if its there'
  current_labels = issue.fields.labels
  if label_to_remove in current_labels:
    current_labels.remove(label_to_remove)
    issue.update(fields={'labels': current_labels})

def return_component_lead(comp_name, project_code ,jira=j.setup_jira_object()):
  #look for component lead
  for comp in jira.project_components(project_code):
    if comp_name == str(comp.name):
        if comp.lead.name:
          return comp.lead.name
        else:
          return False

def update_doc_trigger_status(jira_key, jira=j.setup_jira_object()):
  payload = generate_payload_by_id.generate_payload(jira_key)
  # when a doc project jira is closed, update the linked jira about it
  if payload['status'] == 'Done' and payload['project_name'] == 'DOC' and payload['linked_issue_tree']:
    for linked_issue in payload['linked_issue_tree']:
      if linked_issue['type']['inward'] == 'is caused by':
        action_issue = jira.issue(linked_issue['inwardIssue']['key'])
        #this part will handle new projects
        if action_issue.fields.project.key in ['APPS','CORE','CLD','PROD','SDK']:
          if action_issue.fields.customfield_12043.value != 'Updated':
            print 'DOC issue resolved, Will try to update', action_issue.key
            action_issue.update(fields={'customfield_12043': {'value': 'Updated'}})
            
def get_parent_issue(jira_key, jira=j.setup_jira_object()):
  payload = generate_payload_by_id.generate_payload(jira_key)
  action_issue = None
  if payload['linked_issue_tree']:
    for linked_issue in payload['linked_issue_tree']:
      if linked_issue['type']['inward'] == 'is caused by':
        action_issue = jira.issue(linked_issue['inwardIssue']['key'])
  return action_issue

def is_all_sni_child_stories_done(parent_issue, jira=j.setup_jira_object()):
  linked_sni_issues = check_for_linked_issue_by_project(parent_issue.key, jira, 'SNI')
  all_child_stories_done = True
  for linked_issue_key in linked_sni_issues:
    linked_issue_payload = generate_payload_by_id.generate_payload(linked_issue_key)
    if linked_issue_payload['status'] != 'Done':
      all_child_stories_done = False
      break
  return all_child_stories_done