#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import sys
import json

def findNewPR(pr_list, triggerState):
    prId = triggerState
    sourceBranch, targetBranch = ''
    # loop over all open PRs and pick the next higher PR id
    for prs in info["values"]:
        if prs['id'] > triggerState:
            prId = prs['id']
            sourceBranch = prs['fromRef']['displayId']
            targetBranch = prs['toRef']['displayId']
    return prId, sourceBranch, targetBranch

if server is None:
    print "No Bitbucket server provided."
    sys.exit(1)

request = HttpRequest(server, username, password)
context = "/rest/api/1.0/projects/%s/repos/%s" % (project, repository)
pr_path = "%s/%s" % (context, "pull-requests?order=NEWEST")
response = request.get(pr_path, contentType = 'application/json')

if not response.isSuccessful():
    if response.status == 404 and triggerOnInitialPublish:
        print "Repository '%s:%s' not found in bitbucket. Ignoring." % (project, repository)
        if not triggerState:
            prId = triggerState = 0
    else:
        print "Failed to fetch pr information from Bitbucket server %s" % server['url']
        response.errorDump()
    sys.exit(1)
else:
    info = json.loads(response.response)
    prId, sourceBranch, targetBranch = findNewPR(info, triggerState)
    if prId != triggerState:
        triggerState = prId
        print("Bitbucket triggered release for PR# %s (%s -> %s)" % (prId, sourceBranch, targetBranch))
'''
    # build a map of the commit ids for each branch
    newCommit = {}
    for prs in info["values"]:
        if branch["displayId"] not in excludeBranches.strip(" ").strip(",").split(","):
            branchid = branch["displayId"]
            lastcommit = branch["latestCommit"]
            newCommit[branchid] = lastcommit

    # trigger state is perisisted as json
    newTriggerState = json.dumps(newCommit)

    if triggerState != newTriggerState:
        if len(triggerState) == 0:
            oldCommit = {}
        else:
            oldCommit = json.loads(triggerState)

        branch, commitId = findNewCommit(oldCommit, newCommit)

        if not branchName or (branchName and branchName == branch ):
            triggerState = newTriggerState
            print("Bitbucket triggered release for %s-%s" % (branch, commitId))
'''
