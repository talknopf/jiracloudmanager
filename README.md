# jiracloudmanager

# What is Jira Cloud Manager (or JCM in short)?

This tool serves to resolve an issue anyone working with jira might encounter rather quickly.
JIRA includes workflows that can trigger actions in a sequence,
there are certain workflows that JIRA doesn't support in its workflow.

So, why not a buy a plugin?

I had two reasons - it costs money, and I would rather code it myself.

# So, how does JCM work?

In short, webhooks tell this tool what happens and the tool uses the JIRA API to take action.

But to be more in depth:

1. JIRA sends a webhook to the URL where this code is hosted (will work on anything able to run python flask).
2. In turn the code decides if any action is needed and initiates the action with a 'service user'.

# What do you need to set up for it to work?

1. A JIRA user with API permissions.
2. Webhooks for the actions you want to initiate, for example a webhook for new issues and updated issues.
   
# Is all of the code working out of the box?

No, in few locations you have to provide your own project names, components names, and of course your actions.

# What can we expect next?

Well, as this project is alive and kicking, I am working constantly to add features and integrations. 
I am open to requests and I welcome PRs for bugs, fixes, and new features.
