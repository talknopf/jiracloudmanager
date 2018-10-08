# jiracloudmanager

# What is Jira Cloud Manager (or JCM in short)?
This tool serves to resolve an issue anyone working with jira might encounter rather quickly
although Jira has a notion of a workflow and what comes first and a rather simple way to create hierarchy for multiple projects and ongoing efforts in each.

what it lacks is a to make things happen based on certain scenarios.
so, why not a scripting plugin?

I had two reasons,
  1.It costs money
  2.I would rather code it myself.

# So, how does it work?
In short, webhooks tell this tool what happens and the tool uses jira api to take action.
But to be more in depth, Jira send out a webhook to the url of wherever you hosted this code(will work on anything able to run python flask)
In turn the code will decide if any action is needed and execute it via a 'service user'

# what do you need to set up for it to work?\
1. In jira you will need a user with an API permissions
2. Webhooks for the actions you wish to act upon, in my case the approche was to generate a call for all events.
   using a webhook for new issues and updated issues.
   
# Is all of the code working out of the box?
No, in few location you will have to provide your own project names and components names and ofcourse you decisions.

# What can we expect next?
Well, as this project is alive and kicking. and I am working constently to add features and integrations 
I am open to requests and I welcome PR for bugs, fixes and feature additions.

