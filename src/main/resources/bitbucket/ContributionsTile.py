#
# Copyright 2020 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from bitbucket.Bitbucket import BitbucketClient
import json

if server == "" or repo_full_name == "":
    values = []
    data = {"commits": values}
else:
    bitbucket = BitbucketClient.get_client(server, username, password)
    data = bitbucket.bitbucket_querycommits(locals())
    commits = data

authors = {}
committers = {}
people = []
for commit in commits:
    print "commit: %s" % json.dumps(commit, indent=4, sort_keys=True)
    if commit["author"]["user"]["nickname"] in authors.keys():
        authors[commit["author"]["user"]["nickname"]] += 1
    else:
        authors[commit["author"]["user"]["nickname"]] = 1
    if commit["author"]["user"]["nickname"] not in people:
        people.append(commit["author"]["user"]["nickname"])

    if commit["author"]["user"]["nickname"] in committers.keys():
        committers[commit["author"]["user"]["nickname"]] += 1
    else:
        committers[commit["author"]["user"]["nickname"]] = 1
    if commit["author"]["user"]["nickname"] not in people:
        people.append(commit["author"]["user"]["nickname"])

data = {
    "commits": commits,
    "authors": [
        {"name": author, "value": authors[author]} for author in authors.keys()
    ],
    "committers": [
        {"name": committer, "value": committers[committer]}
        for committer in committers.keys()
    ],
    "people": people,
}
