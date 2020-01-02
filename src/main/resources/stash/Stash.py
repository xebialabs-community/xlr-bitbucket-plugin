# Copyright 2020 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import json, time, re
from xlrelease.HttpRequest import HttpRequest
from xlrelease.CredentialsFallback import CredentialsFallback
from org.apache.http.client import ClientProtocolException
from com.xebialabs.overthere import CmdLine
from com.xebialabs.overthere.util import CapturingOverthereExecutionOutputHandler, OverthereUtils
from com.xebialabs.overthere.local import LocalConnection
from java.lang import String
import httplib
from base64 import b64encode
import org.slf4j.Logger as Logger
import org.slf4j.LoggerFactory as LoggerFactory


class StashClient(object):
    def __init__(self, server, username, password):
        self.logger = LoggerFactory.getLogger("com.xebialabs.bitbucket-plugin")
        creds = CredentialsFallback(server, username, password).getCredentials()
        self.http_request = HttpRequest(server, creds['username'], creds['password'])

    @staticmethod
    def get_client(server, username, password):
        return StashClient(server, username, password)

    def parse_output(self, lines):
        result_output = ""
        for line in lines:
            result_output = '\n'.join([result_output, line])
        return result_output

    def api_call(self, method, endpoint, **options):

        try:
            options['method'] = method.upper()
            options['context'] = endpoint
            #self.logger.warn( options )
            print options
            response = self.http_request.doRequest(**options)
        except ClientProtocolException:
            raise Exception("URL is not valid")
        if not response.isSuccessful():
            raise Exception("HTTP response code %s (%s)" % (response.getStatus(), response.errorDump()))
        return response

    def stash_createpullrequest(self, variables):
        endpoint="/rest/api/1.0/projects/%s/repos/%s/pull-requests" % (variables['project'], variables['repository'])
        content = '''{
            "title": "%s",
            "description": "%s",
            "fromRef": {
                "id": "refs/heads/%s"
            },
            "toRef": {
                "id": "refs/heads/%s"
            }
        }''' % (str(variables['title']),
                str(variables['description']),
                str(variables['source']),
                str(variables['target']))
        self.logger.warn( "Submitting Pull Request %s using endpoint %s" % (content, endpoint) )
        response = self.api_call('POST',endpoint, body = content, contentType="application/json")
        data = json.loads(response.getResponse())
        self.logger.warn( "Pull Request created with ID %s " % data['id'] )
        return {'output' : data, 'prid' : data['id']}

    def stash_mergepullrequest(self, variables):
        endpoint_get = "/rest/api/1.0/projects/%s/repos/%s/pull-requests/%s" % (variables['project'], variables['repository'], str(variables['prid']))
        self.logger.warn( "Getting Pull Request %s current version using endpoint %s" % (str(variables['prid']), endpoint_get) )
        response = self.api_call('GET', endpoint_get, contentType="application/json")
        data = json.loads(response.getResponse())
        content = '{}'
        endpoint_post = "/rest/api/1.0/projects/%s/repos/%s/pull-requests/%s/merge?version=%s" % (variables['project'], variables['repository'], str(variables['prid']), data['version'])
        self.logger.warn( "Merging Pull Request %s using endpoint %s" % (str(variables['prid']), endpoint_post) )
        response = self.api_call('POST',endpoint_post,body=content, contentType="application/json")
        data = json.loads(response.getResponse())
        self.logger.warn( "Pull Request %s merged sucessfully with STATE : %s" % ( data['id'], data['state']) )
        return {'output' : data}

    def stash_declinepullrequest(self, variables):
        endpoint_get = "/rest/api/1.0/projects/%s/repos/%s/pull-requests/%s" % (variables['project'], variables['repository'], str(variables['prid']))
        self.logger.warn( "Getting Pull Request %s current version using endpoint %s" % (str(variables['prid']), endpoint_get) )
        response = self.api_call('GET', endpoint_get, contentType="application/json", Origin = variables['server']['url'])
        data = json.loads(response.getResponse())
        content = '{}'
        endpoint_post = "/rest/api/1.0/projects/%s/repos/%s/pull-requests/%s/decline?version=%s" % (variables['project'], variables['repository'], str(variables['prid']), data['version'])
        self.logger.warn( "Declining Pull Request %s using endpoint %s" % (str(variables['prid']), endpoint_post) )
        response = self.api_call('POST',endpoint_post,body=content, contentType="application/json")
        data = json.loads(response.getResponse())
        self.logger.warn( "Pull Request %s decline sucessfully with STATE : %s" % ( data['id'], data['state']) )
        return {'output' : data}

    def stash_getpullrequest(self, variables):
        endpoint_get = "/rest/api/1.0/projects/%s/repos/%s/pull-requests/%s" % (variables['project'], variables['repository'], str(variables['prid']))
        self.logger.warn( "Getting Pull Request %s current version using endpoint %s" % (str(variables['prid']), endpoint_get) )
        response = self.api_call('GET', endpoint_get, contentType="application/json", Origin = variables['server']['url'])
        data = response.getResponse()
        return {'output' : data}

    def stash_searchfilecontent(self,variables):
        endpoint = "/rest/api/1.0/projects/%s/repos/%s/browse/%s?at=refs/heads/%s" % (variables['project'], variables['repository'], str(variables['filepath']), variables['branch'])
        self.logger.warn( "Parsing file content for file :%s for branch %s" % (str(variables['filepath']), variables['branch'] ) )
        response = self.api_call('GET', endpoint, contentType="application/json")
        data = json.loads(response.getResponse())
        pattern = re.compile(variables['pattern'])
        for item in data['lines']:
            result = pattern.search(item['text'])
            if result != None and len(result.groups()) == 1:
                return {'group0' : result.group(0), 'group1' : result.group(1)}


    def stash_waitformerge(self, variables):
        endpoint = "/rest/api/1.0/projects/%s/repos/%s/pull-requests/%s" % (variables['project'], variables['repository'], str(variables['prid']))
        self.logger.warn( "Waiting for Merge Pull Request %s using endpoint %s" % (str(variables['prid']), endpoint) )
        isClear = False
        while (not isClear):
            response = self.api_call('GET',endpoint, contentType="application/json")
            data = json.loads(response.getResponse())
            if data['state'] == "MERGED" :
                isClear = True
                self.logger.warn( "Pull Request %s merged sucessfully with STATE : %s" % (data['id'], data['state']) )
            else:
                self.logger.warn( "Pull Request %s : current STATE :[ %s ], retrying after %s seconds\n" % (data['id'], data['state'], str(variables['pollInterval']) ) )
                time.sleep(variables['pollInterval'])
        return {'output' : data}

    def stash_tagrelease(self, variables):
        endpoint = "/rest/git/1.0/projects/%s/repos/%s/tags" % (variables['project'], variables['repository'])
        self.logger.warn("Tag project (%s/%s" % (variables['project'], variables['repository']))
        content = '''{"force":"true", "message":"%s", "name":"%s", "startPoint":"refs/heads/%s", "type":"ANNOTATED"}''' % (variables['message'], variables['tagname'], variables['branch'])
        response = self.api_call('POST',endpoint,body=content, contentType="application/json")
        data = response.getResponse()
        return {'output': data}


    # TODO -  apache cleint doesnt support body with DELETE method. add ability to xlrelease.HTTPRequest
    def stash_deletebranch_old(self, variables):
        endpoint = "/rest/branch-utils/1.0/projects/%s/repos/%s/branches" % (variables['project'], variables['repository'])
        content = '''{"name": "refs/heads/%s"}''' % (variables['branch'])
        self.logger.warn( "Deleting %s using endpoint %s" % (content, endpoint) )
        response = self.api_call('DELETE', endpoint, body = content, contentType="application/json", Origin = variables['server']['url'])
        if response.getStatus() == "204 No Content" :
            self.logger.warn( "Successfully deleted branch %s " % ( variables['branch']) )
            return {}
        else:
            raise Exception(" Not able to delete branch %s " % ( variables['branch']) )

    def stash_deletebranch(self, variables):
        endpoint = "/rest/branch-utils/1.0/projects/%s/repos/%s/branches" % (
        variables['project'], variables['repository'])
        content = '''{"name": "refs/heads/%s"}''' % (variables['branch'])
        self.logger.warn( "Deleting %s using endpoint %s" % (content, endpoint) )
        url_split = variables['server']['url'].split("://")
        userAndPass = b64encode(b"%s:%s" % (self.http_request.username, self.http_request.password)).decode("ascii")
        headers = {'Authorization': 'Basic %s' % userAndPass, 'Content-Type':'application/json'}
        if url_split[0].lower() == "http":
            conn = httplib.HTTPConnection(url_split[1])
        else:
            conn = httplib.HTTPSConnection(url_split[1])
        conn.request('DELETE', endpoint, content, headers=headers)
        response =conn.getresponse()
        if str(response.status) == "204":
            self.logger.warn( "Successfully deleted branch %s " % (variables['branch']) )
            return {}
        else:
            raise Exception(" Not able to delete branch %s , Response Code : %s " % (variables['branch'], response.status) )

    # Requires the stash archive plugin installed
    def stash_downloadcode(self, variables):
        downloadURL = "%s/rest/archive/latest/projects/%s/repos/%s/archive?at=refs/heads/%s&format=zip" % (variables['server']['url'], variables['project'],variables['repository'], variables['branch'] )
        connection = LocalConnection.getLocalConnection()

        capturedOutput = ""

        self.logger.warn( "Cleaning up download folder : %s" % variables['downloadPath'] )
        command = CmdLine()
        command.addArgument("mkdir")
        command.addArgument("-p")
        command.addArgument(variables['downloadPath'])
        output_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        error_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        exit_code = connection.execute(output_handler, error_handler, command)
        capturedOutput = self.parse_output(output_handler.getOutputLines()) + self.parse_output(error_handler.getOutputLines())

        self.logger.warn( " Now downloading code in download folder : %s" % variables['downloadPath'] )
        command = CmdLine()
        script = '''
            cd %s
            ls | grep -v extract.sh | xargs rm -rf
            wget --user %s --password %s  -O code.zip '%s'
            unzip -o code.zip
            rm code.zip
        ''' % (variables['downloadPath'], self.http_request.username, self.http_request.password,  downloadURL )
        script_file = connection.getFile(OverthereUtils.constructPath(connection.getFile(variables['downloadPath']), 'extract.sh'))
        OverthereUtils.write(String(script).getBytes(), script_file)
        script_file.setExecutable(True)
        command.addArgument(script_file.getPath())
        output_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        error_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        exit_code = connection.execute(output_handler, error_handler, command)
        capturedOutput += self.parse_output(output_handler.getOutputLines()) + self.parse_output(error_handler.getOutputLines())

        command = CmdLine()
        command.addArgument("rm")
        command.addArgument("-f")
        command.addArgument(variables['downloadPath'] + "/extract.sh")
        output_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        error_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        exit_code = connection.execute(output_handler, error_handler, command)
        capturedOutput += self.parse_output(output_handler.getOutputLines()) + self.parse_output(error_handler.getOutputLines())

        return {'output': capturedOutput}

    def stash_commitsquery(self, variables):
        variables['slug'] = variables['repository']
        data = json.loads(self.stash_querycommits(variables))
        commits = data['parents']
        self.logger.warn( "Build commitList\n %s" % commits )
        commitList = []
        for commit in commits:
            self.logger.warn( "~%s~" %  commit['message'] )
            commitList.append( commit['message'] )
        results = { "output": data, "commitList": commitList }
        return results

    # Requires the stash archive plugin installed
    def stash_querycommits(self, variables):
        endpoint_get = "/rest/api/1.0/projects/%s/repos/%s/commits" % (variables['project'], variables['slug'])
        if variables['branch'] is not None:
            endpoint_get = "%s/%s" % (endpoint_get, variables['branch'])
        endpoint_get = "%s/?limit=%s" % (endpoint_get, variables['results_limit'])
        if ( variables['tag'] is not None ):
            endpoint_get = "%s&at=refs/tags/%s" % (endpoint_get, variables['tag'])
        response = self.api_call('GET', endpoint_get, contentType="application/json", Origin = variables['server']['url'])
        data = response.getResponse()
        self.logger.warn( "endpint = %s" % endpoint_get )
        self.logger.warn( "DATA2 = %s" %  json.dumps(json.loads(data), indent=4, sort_keys=True) )
        return data

    def stash_querymergerequests(self, variables):
        endpoint = "/rest/api/1.0/projects/%s/repos/%s/pull-requests?state=%s&limit=100" % (variables['project'], variables['slug'], variables['state'])
        self.logger.warn( "URL = %s" % endpoint )
        response = self.api_call('GET', endpoint, contentType="application/json", Origin = variables['server']['url'])
        data = response.getResponse()
        self.logger.warn( "merge_requests = %s" % json.dumps(json.loads(data), indent=4, sort_keys=True) )
        return data
