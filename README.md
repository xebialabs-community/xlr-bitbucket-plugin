# XLR Bitbucket plugin

[![Build Status][xlr-bitbucket-plugin-travis-image]][xlr-bitbucket-plugin-travis-url]
[![Codacy Badge][xlr-bitbucket-plugin-codacy-image] ][xlr-bitbucket-plugin-codacy-url]
[![Code Climate][xlr-bitbucket-plugin-code-climate-image] ][xlr-bitbucket-plugin-code-climate-url]
[![License: MIT][xlr-bitbucket-plugin-license-image] ][xlr-bitbucket-plugin-license-url]
[![Github All Releases][xlr-bitbucket-plugin-downloads-image] ]()

[xlr-bitbucket-plugin-travis-image]: https://travis-ci.org/xebialabs-community/xlr-bitbucket-plugin.svg?branch=master
[xlr-bitbucket-plugin-travis-url]: https://travis-ci.org/xebialabs-community/xlr-bitbucket-plugin
[xlr-bitbucket-plugin-codacy-image]: https://api.codacy.com/project/badge/Grade/0e664aaacd2f4010b091f0ef4ce1c7d0
[xlr-bitbucket-plugin-codacy-url]: https://www.codacy.com/app/amitmohleji/xlr-bitbucket-plugin
[xlr-bitbucket-plugin-code-climate-image]: https://codeclimate.com/github/xebialabs-community/xlr-bitbucket-plugin/badges/gpa.svg
[xlr-bitbucket-plugin-code-climate-url]: https://codeclimate.com/github/xebialabs-community/xlr-bitbucket-plugin
[xlr-bitbucket-plugin-license-image]: https://img.shields.io/badge/License-MIT-yellow.svg
[xlr-bitbucket-plugin-license-url]: https://opensource.org/licenses/MIT
[xlr-bitbucket-plugin-downloads-image]: https://img.shields.io/github/downloads/xebialabs-community/xlr-bitbucket-plugin/total.svg

This plugin offers an interface from XL Release to Atlassian Stash(Now Bitbucket Server) and Bitbucket Cloud API

#### IMPORTANT ####

* Use **Stash Connection and Stash Tasks** if you're using an **on-prem hosted Bitbucket Server**. Stash is now called Bitbucket Server.  
* Use **Bitbucket Connection and Bitbucket Tasks** if you're using **Bitbucket Cloud**.
* All Stash/Bitbucket Server tasks are based on api **/rest/api/1.0/** prefix  
* All Bitbucket Cloud tasks are based on api **/2.0/** prefix


# Development #

* Start XLR: `./gradlew runDockerCompose`

# Type definitions #

### Commit Pull Triggers ###

+ `bitbucket.CommitTrigger` : This trigger can be used to poll Bitbucket cloud for triggering releases on code commit
+ `stash.CommitTrigger` :  This trigger can be used to poll Stash for triggering releases on code commit

### Webhook (Push) ###

+ **Stash Push Webhook** `http://<xlr server:port>/api/extension/stash/push_webhook?template=<template name>` : This can be used to push Commit notifications across branches in a repository. Requires [Web POST Hooks Plugin](https://marketplace.atlassian.com/plugins/com.atlassian.stash.plugin.stash-web-post-receive-hooks-plugin/server/overview)
+ **Stash Pull Request Webhook** `http://<xlr server:port>/api/extension/stash/pr_webhook?template=<template name>` : This can be used to push Pull Request notifications. Requires [Pull Request Notifier Plugin](https://marketplace.atlassian.com/plugins/se.bjurr.prnfs.pull-request-notifier-for-stash/server/overview)
	* Method : POST
	* Provide Auth using XLR Credentials
	* Provide Header :: Content-Type : application/json 
	* Trigger Condition :  PR OPENED
	* Select Option : Encode HTML ( so that commit squash line breaks get encoded)
	* POST Body Content:
	
	```
		{ "push":"true",
	    "pr_number":"${PULL_REQUEST_ID}",
	    "repository":"${PULL_REQUEST_FROM_REPO_SLUG}",
	    "proj": "${PULL_REQUEST_FROM_REPO_PROJECT_KEY}",
	    "pr_title":"${PULL_REQUEST_TITLE}",
	    "comment" :"${PULL_REQUEST_DESCRIPTION}",
	    "source_hash":"${PULL_REQUEST_FROM_HASH}",
	    "source_branch":"${PULL_REQUEST_FROM_BRANCH}",
	    "source_project":"${PULL_REQUEST_FROM_REPO_PROJECT_KEY}",
	    "source_repo":"${PULL_REQUEST_FROM_REPO_SLUG}",
	    "target_hash": "${PULL_REQUEST_TO_HASH}",
	    "target_branch":"${PULL_REQUEST_TO_BRANCH}",
	    "target_project":"${PULL_REQUEST_TO_REPO_PROJECT_KEY}",
	    "target_repo":"${PULL_REQUEST_TO_REPO_SLUG}"
	    }
	```
+ **Bitbucket Push Webhook** `http://<xlr server:port>/api/extension/bitbucket/push_webhook?template=<template name>` : This can be used to push Commit notifications across branches in a repository.

### Bitbucket Tasks ###

+ `bitbucket.CreatePullRequest` : This task helps to create a pull request
+ `bitbucket.MergePullRequest` : This task helps to Merge a pull request
+ `bitbucket.WaitForMerge` : This task waits and polls bitbucket to check the status of a Pull request Merge Status
+ `bitbucket.DownloadCode` : This task allows to export a code zip file that can be downloaded to a specified folder on XL Release server locally for a provided branch in repository

### Stash Tasks ###    

+ `stash.CreatePullRequest` : This task helps to create a pull request
+ `stash.MergePullRequest` : This task helps to Merge a pull request
+ `stash.DeclinePullRequest` : This task can be used to Decline a pull request
+ `stash.WaitForMerge` : This task waits and polls stash to check the status of a Pull request Merge Status
+ `stash.DownloadCode` : This task allows to export a code zip file that can be downloaded to a specified folder on XL Release server locally for a provided branch in repository. Requires [Bitbucket Server Archive plugin](https://marketplace.atlassian.com/plugins/com.atlassian.stash.plugin.stash-archive/server/overview)
+ `stash.searchFileContent` : This task allows to search a file's content in a repository/branch using a provided pattern and return group0 and group1 as results. eg. 

	```
	version[ ]*=[ ]*(\d+)

	```

+ `stash.DeleteBranch` : This task allows to delete a branch
+ `stash.TagRelease` : This task adds a tag to a branch


    
# Commit Trigger Usage #

* Stash commit trigger configuration

![](images/stash/stashcommittrigger1.png)

![](images/stash/stashcommittrigger2.png)

# Bitbucket Tasks Usage #
   
* Setup the server configuration

![](images/bitbucket/config.png)

* Create pull request 

![](images/bitbucket/createpullrequest.png)

* Merge pull request

![](images/bitbucket/mergepullrequest.png)

* Wait for merge

![](images/bitbucket/waitformerge.png)

* Download Code 

![](images/bitbucket/downloadcodezip.png)


# Stash Tasks Usage #

   
* Setup the server configuration

![](images/stash/config.png)

* Create pull request 

![](images/stash/createpullrequest.png)

* Merge pull request

![](images/stash/mergepullrequest.png)

* Wait for merge
![](images/stash/waitformerge.png)

* Decline pull request

![](images/stash/declinepullrequest.png)

* Delete branch 

![](images/stash/deletebranch.png)

* Search file content

![](images/stash/searchfilecontent.png)

* Download Code 

![](images/stash/downloadcodezip.png)

* Get Pull Request

![](images/stash/getpullrequest.png)

* Tag Release

![](images/stash/tagrelease.png)

# References #

[Stash/Bitbucket Server REST API](https://developer.atlassian.com/stash/docs/latest/reference/rest-api.html)  
[Bitbucket Cloud REST API](https://confluence.atlassian.com/bitbucket/use-the-bitbucket-cloud-rest-apis-222724129.html)

