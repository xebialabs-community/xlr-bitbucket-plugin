#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

###################################################################################
#  Name: Bitbucket Commit Trigger
#
#  Description: Trigger new release when new commit is made to a bitbucket repository
#
###################################################################################

import sys
import json

def findNewCommit(oldCommitMap, newCommitMap):
    branch = ""
    commitId = ""

    # loop over new map branches
    for newBranch, newCommitId in newCommitMap.iteritems():
        # check if branch exists in old map
        if newBranch in oldCommitMap:
            oldCommitId = oldCommitMap[newBranch]
            # compare commit ids
            if newCommitId != oldCommitId:
                branch = newBranch
                commitId = newCommitId
                break
        else:
            # new branch, this triggered it
            branch = newBranch
            commitId = newCommitId
            break

    return branch, commitId

if server is None:
    print "No Bitbucket server provided."
    sys.exit(1)

request = HttpRequest(server, username, password)
context = "/rest/api/1.0/projects/%s/repos/%s" % (project, repository)
branches_path = "%s/%s?limit=1000" % (context, "branches")
response = request.get(branches_path, contentType = 'application/json')

if not response.isSuccessful():
    if response.status == 404 and triggerOnInitialPublish:
        print "Repository '%s:%s' not found in bitbucket. Ignoring." % (project, repository)

        if not triggerState:
            branch = commitId = triggerState = 'unknown'
    else:
        print "Failed to fetch branch information from Bitbucket server %s" % server['url']
        response.errorDump()
    sys.exit(1)
else:
    info = json.loads(response.response)

    # build a map of the commit ids for each branch
    newCommit = {}
    for branch in info["values"]:
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
