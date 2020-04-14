#
# Copyright 2020 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import json, time
from xlrelease.HttpRequest import HttpRequest
from xlrelease.CredentialsFallback import CredentialsFallback
from org.apache.http.client import ClientProtocolException
from com.xebialabs.overthere import CmdLine
from com.xebialabs.overthere.util import CapturingOverthereExecutionOutputHandler, OverthereUtils
from com.xebialabs.overthere.local import LocalConnection
from com.xebialabs.overthere.OperatingSystemFamily import UNIX
from java.lang import String
import org.slf4j.Logger as Logger
import org.slf4j.LoggerFactory as LoggerFactory

class BitbucketClient(object):
    def __init__(self, server, username, password):
        self.logger = LoggerFactory.getLogger("com.xebialabs.bitbucket-plugin")
        creds = CredentialsFallback(server, username, password).getCredentials()
        self.http_request = HttpRequest(server, creds['username'], creds['password'])

    @staticmethod
    def get_client(server, username, password):
        return BitbucketClient(server, username, password)

    def parse_output(self, lines):
        result_output = ""
        for line in lines:
            result_output = '\n'.join([result_output, line])
        return result_output

    def api_call(self, method, endpoint, **options):
        try:
            options['method'] = method.upper()
            options['context'] = endpoint
            response = self.http_request.doRequest(**options)
        except ClientProtocolException:
            raise Exception("URL is not valid")
        if not response.isSuccessful():
            raise Exception("HTTP response code %s (%s)" % (response.getStatus(), response.errorDump()))
        return response

    def bitbucket_createpullrequest(self, variables):
        endpoint = "/2.0/repositories/%s/pullrequests" % str(variables['repo_full_name'])
        content = '''{
            "title": "%s",
            "description": "%s",
            "source": {
                "branch": {
                    "name": "%s"
                }
            },
            "destination": {
                "branch": {
                    "name": "%s"
                }
            },
            "close_source_branch": %s
        }''' % (str(variables['title']),
                str(variables['description']),
                str(variables['source']),
                str(variables['target']),
                str(variables['closebranch']).lower())
        self.logger.warn(  "Submitting Pull Request %s using endpoint %s" % (content, endpoint) )
        response = self.api_call('POST',endpoint, body = content, contentType="application/json")
        data = json.loads(response.getResponse())
        self.logger.warn( "Pull Request created with ID %s " % data['id'] )
        return {'output' : data, 'prid' : data['id']}

    def bitbucket_mergepullrequest(self, variables):
        endpoint = "/2.0/repositories/%s/pullrequests/%s/merge" % (str(variables['repo_full_name']), str(variables['prid']))
        content = '''{
            "message": "%s",
            "close_source_branch": %s
        }''' % (str(variables['message']),
                str(variables['closebranch']).lower())
        self.logger.warn( "Merging Pull Request %s using endpoint %s" % (content, endpoint) )
        response = self.api_call('POST',endpoint, body = content, contentType="application/json")
        data = json.loads(response.getResponse())
        self.logger.warn( "Pull Request %s merged sucessfully with STATE : %s" % ( data['id'], data['state']) )
        return {'output' : data}

    def bitbucket_waitformerge(self, variables):
        endpoint = "/2.0/repositories/%s/pullrequests/%s" % (str(variables['repo_full_name']), str(variables['prid']))
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

    def bitbucket_downloadcode(self, variables):
        downloadURL = "%s/%s/get/%s.zip" % (variables['server']['url'].replace("api.","www."), variables['repo_full_name'], variables['branch'] )
        connection = LocalConnection.getLocalConnection()

        capturedOutput = ""

        self.logger.warn( "Cleaning up download folder : %s" % variables['downloadPath'] )
        command = CmdLine()
        command.addArgument("rm")
        command.addArgument("-rf")
        command.addArgument(variables['downloadPath'] + "/*")
        output_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        error_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        exit_code = connection.execute(output_handler, error_handler, command)
        capturedOutput = self.parse_output(output_handler.getOutputLines()) + self.parse_output(error_handler.getOutputLines())

        self.logger.warn( " Now downloading code in download folder : %s" % variables['downloadPath'] )
        command = CmdLine()
        script = '''
            cd %s
            wget --user %s --password %s  -O code.zip %s
            unzip code.zip
            rm -rf *.zip
            foldername=`ls -d */`
            mv -f $foldername* `pwd`
            rm -rf $foldername
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

    def bitbucket_commitsquery(self, variables):
        self.logger.warn("bitbucket_commitsquery-> START")
        data = self.bitbucket_querycommits(variables)
        commits = data
        #self.logger.warn( "Build commitList\n %s" % json.dumps(commits, indent=4, sort_keys=True) )
        commitList = []
        self.logger.warn("bitbucket_commitsquery-> Loop over commits")
        for commit in commits:
            self.logger.warn( "message ~%s~" %  commit['message'] )
            commitList.append( commit['message'] )
        results = { "output": data, "commitList": commitList }
        self.logger.warn( "results\n %s" % json.dumps(results, indent=4, sort_keys=True) )
        return results

    def bitbucket_querycommits(self, variables):
        endpoint_get = "/2.0/repositories/%s/commits/%s" % (variables['repo_full_name'], variables['branch'] )
        endpoint_get = "%s?limit=%s" % (endpoint_get, variables['results_limit'])
        if ( variables['tag'] is not None ):
            endpoint_get = "%s&at=refs/tags/%s" % (endpoint_get, variables['tag'])
        self.logger.warn( "endpoint = %s" % endpoint_get )
        response = self.api_call('GET', endpoint_get, contentType="application/json", Origin = variables['server']['url'])
        data = response.getResponse()
        data = json.loads(data)['values']
        self.logger.warn( "DATA2 = %s" %  json.dumps(data, indent=4, sort_keys=True) )
        return data

    def bitbucket_querymergerequests(self, variables):
        endpoint = "2.0/repositories/%s/pullrequests?state=%s" % (variables['repo_full_name'], variables['state'])
        self.logger.warn( "URL = %s" % endpoint )
        response = self.api_call('GET', endpoint, contentType="application/json", Origin = variables['server']['url'])
        data = json.loads( response.getResponse() )['values']
        self.logger.warn( "merge_requests = %s" % json.dumps(data, indent=4, sort_keys=True) )
        return data
