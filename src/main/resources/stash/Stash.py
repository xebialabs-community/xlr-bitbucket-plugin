#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
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


class StashClient(object):
    def __init__(self, server, username, password):
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
        print "Submitting Pull Request %s using endpoint %s" % (content, endpoint)
        response = self.api_call('POST',endpoint, body = content, contentType="application/json")
        data = json.loads(response.getResponse())
        print "Pull Request created with ID %s " % data['id']
        return {'output' : data, 'prid' : data['id']}

    def stash_mergepullrequest(self, variables):
        endpoint = "/rest/api/1.0/projects/%s/repos/%s/pull-requests/%s/merge" % (variables['project'], variables['repository'], str(variables['prid']))
        content = None
        print "Merging Pull Request %s using endpoint %s" % (content, endpoint)
        response = self.api_call('POST',endpoint, body = content, contentType="application/json")
        data = json.loads(response.getResponse())
        print "Pull Request %s merged sucessfully with STATE : %s" % ( data['id'], data['state'])
        return {'output' : data}

    def stash_waitformerge(self, variables):
        endpoint = "/rest/api/1.0/projects/%s/repos/%s/pull-requests/%s" % (variables['project'], variables['repository'], str(variables['prid']))
        print "Waiting for Merge Pull Request %s using endpoint %s" % (str(variables['prid']), endpoint)
        isClear = False
        while (not isClear):
            response = self.api_call('GET',endpoint, contentType="application/json")
            data = json.loads(response.getResponse())
            if data['state'] == "MERGED" :
                isClear = True
                print "Pull Request %s merged sucessfully with STATE : %s" % (data['id'], data['state'])
            else:
                print "Pull Request %s : current STATE :[ %s ], retrying after %s seconds\n" % (data['id'], data['state'], str(variables['pollInterval']) )
                time.sleep(variables['pollInterval'])
        return {'output' : data}

    # Requires the stash archive plugin installed
    def stash_downloadcode(self, variables):
        downloadURL = "%s/rest/archive/latest/projects/%s/repos/%s/archive?at=refs/heads/%s&format=zip" % (variables['server']['url'], variables['project'],variables['repository'], variables['branch'] )
        connection = LocalConnection.getLocalConnection()

        capturedOutput = ""

        print "Cleaning up download folder : %s" % variables['downloadPath']
        command = CmdLine()
        command.addArgument("rm")
        command.addArgument("-rf")
        command.addArgument(variables['downloadPath'] + "/*")
        output_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        error_handler = CapturingOverthereExecutionOutputHandler.capturingHandler()
        exit_code = connection.execute(output_handler, error_handler, command)
        capturedOutput = self.parse_output(output_handler.getOutputLines()) + self.parse_output(error_handler.getOutputLines())

        print " Now downloading code in download folder : %s" % variables['downloadPath']
        command = CmdLine()
        script = '''
            cd %s
            wget --user %s --password %s  -O code.zip %s
            unzip code.zip
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



