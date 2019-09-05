#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from stash.Stash import StashClient
import datetime

def convertMillisEpoch(millis):
    return datetime.datetime.fromtimestamp(float(millis)/1000).strftime('%Y-%m-%d %H:%M:%S %Z')

stash = StashClient.get_client(server, username, password)
method = "stash_querycommits"
call = getattr(stash, method)
response = call(locals())

commits = response["output"]

# Compile data for detail and summary views
authors = {}
committers = {}
people = []
for commit in commits:
    if commit["author"]["name"] in authors.keys():
        authors[commit["author"]["name"]] += 1
    else:
        authors[commit["author"]["name"]] = 1
    if commit["author"]["name"] not in people:
        people.append(commit["author"]["name"])

    if commit["committer"]["name"] in committers.keys():
        committers[commit["committer"]["name"]] += 1
    else:
        committers[commit["committer"]["name"]] = 1
    if commit["committer"]["name"] not in people:
        people.append(commit["committer"]["name"])

# Convert timestamps to a user-friendly format
for i in range(len(commits)):
    commits[i]["authorTimestamp"] = convertMillisEpoch(commits[i]["authorTimestamp"])
    commits[i]["committerTimestamp"] = convertMillisEpoch(commits[i]["committerTimestamp"])

data = {
    "commits": commits,
    "authors": [{"name":author,"value":authors[author]} for author in authors.keys()],
    "committers": [{"name":committer,"value":committers[committer]} for committer in committers.keys()],
    "people": people
}