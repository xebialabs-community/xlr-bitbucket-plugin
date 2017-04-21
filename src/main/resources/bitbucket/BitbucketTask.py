#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from bitbucket.Bitbucket import BitbucketClient

bitbucket = BitbucketClient.get_client(server, username, password)
method = str(task.getTaskType()).lower().replace('.', '_')
call = getattr(bitbucket, method)
response = call(locals())
for key,value in response.items():
    locals()[key] = value
