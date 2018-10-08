# -*- coding: utf-8 -*-
import os
import sys
import json

def load_team_members():
  #this section will try and define a map of team members to allow logic based of teams responsiabilities
  try:
    teams = {
      'QA' : [],
      'CTO' : [],
      'Documentation' : [],
      'R&D' : [],
      'product' : []
    }
    
  except Exception as e:
    print "Could not set team members"
  
  return teams

if __name__=='__main__':
	print load_team_members()