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
from java.time import LocalDate

def convertMillisEpochDateComponents(millis):
    isodate = datetime.datetime.fromtimestamp(float(millis)/1000).strftime('%Y-%m-%d').split('-')
    isodate = [int(dateComponent) for dateComponent in isodate]
    return LocalDate.of(isodate[0], isodate[1], isodate[2])

def convertMillisEpoch(millis):
    return datetime.datetime.fromtimestamp(float(millis)/1000).strftime('%Y-%m-%d %H:%M:%S %Z')

stash = StashClient.get_client(server, username, password)
method = "stash_querycommits"
call = getattr(stash, method)
response = call(locals())

commits = response["output"]

# Compile data for summary view
commitsByDay = {}
for commit in commits:
    commitDate = convertMillisEpochDateComponents(commit["committerTimestamp"])
    if commitDate in commitsByDay.keys():
        commitsByDay[commitDate] += 1
    else:
        commitsByDay[commitDate] = 1

dates = [date for date in commitsByDay.keys()]
dates.sort()
startDate = dates[0]
endDate = dates[-1]
days = []
commitsEachDay = []
daysWithCommits = [dayCommits.toString() for dayCommits in commitsByDay.keys()]
while startDate.isBefore(endDate.plusDays(1)):
    days.append(startDate.toString())
    if startDate.toString() in daysWithCommits:
        commitsEachDay.append(commitsByDay[startDate])
    else:
        commitsEachDay.append(0)
    startDate = startDate.plusDays(1)

# Convert timestamps to a user-friendly format for the detail view
for i in range(len(commits)):
    commits[i]["authorTimestamp"] = convertMillisEpoch(commits[i]["authorTimestamp"])
    commits[i]["committerTimestamp"] = convertMillisEpoch(commits[i]["committerTimestamp"])

data = {
    "dates": days,
    "commitsEachDay": commitsEachDay,
    "commits": commits
}