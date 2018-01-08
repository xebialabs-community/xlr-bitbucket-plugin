#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
import tempfile
from com.xebialabs.xlr.ssl import LoaderUtil
from java.nio.file import Files, Paths, StandardCopyOption

import json, time
import requests, zipfile, StringIO
from xlrelease.HttpRequest import HttpRequest
from xlrelease.CredentialsFallback import CredentialsFallback
from org.apache.http.client import ClientProtocolException


class BitbucketClient(object):
    def __init__(self, server, username, password):
        self.creds = CredentialsFallback(server, username, password).getCredentials()
        self.http_request = HttpRequest(server, self.creds['username'], self.creds['password'])

    @staticmethod
    def get_client(server, username, password):
        return BitbucketClient(server, username, password)

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
        print "Submitting Pull Request %s using endpoint %s" % (content, endpoint)
        response = self.api_call('POST', endpoint, body=content, contentType="application/json")
        data = json.loads(response.getResponse())
        print "Pull Request created with ID %s " % data['id']
        return {'output': data, 'prid': data['id']}

    def bitbucket_mergepullrequest(self, variables):
        endpoint = "/2.0/repositories/%s/pullrequests/%s/merge" % (
            str(variables['repo_full_name']), str(variables['prid']))
        content = '''{
            "message": "%s",
            "close_source_branch": %s
        }''' % (str(variables['message']),
                str(variables['closebranch']).lower())
        print "Merging Pull Request %s using endpoint %s" % (content, endpoint)
        response = self.api_call('POST', endpoint, body=content, contentType="application/json")
        data = json.loads(response.getResponse())
        print "Pull Request %s merged successfully with STATE : %s" % (data['id'], data['state'])
        return {'output': data}

    def bitbucket_waitformerge(self, variables):
        endpoint = "/2.0/repositories/%s/pullrequests/%s" % (str(variables['repo_full_name']), str(variables['prid']))
        print "Waiting for Merge Pull Request %s using endpoint %s" % (str(variables['prid']), endpoint)
        is_clear = False
        while not is_clear:
            response = self.api_call('GET', endpoint, contentType="application/json")
            data = json.loads(response.getResponse())
            if data['state'] == "MERGED":
                is_clear = True
                print "Pull Request %s merged successfully with STATE : %s" % (data['id'], data['state'])
            else:
                print "Pull Request %s : current STATE :[ %s ], retrying after %s seconds\n" % (
                    data['id'], data['state'], str(variables['pollInterval']))
                time.sleep(variables['pollInterval'])
        return {'output': data}

    def bitbucket_downloadcode(self, variables):
        session = requests.Session()
        session.auth = (self.creds['username'], self.creds['password'])
        download_url = "%s/%s/get/%s.zip" % (
            variables['server']['url'].replace("api.", ""), variables['repo_full_name'], variables['branch'])
        r = session.get(download_url)
        r.raise_for_status()
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall(variables['downloadPath'])
        return {}


def set_ca_bundle_path():
    ca_bundle_path = extract_file_from_jar("requests/cacert.pem")
    os.environ['REQUESTS_CA_BUNDLE'] = ca_bundle_path


def extract_file_from_jar(config_file):
    file_url = LoaderUtil.getResourceBySelfClassLoader(config_file)
    if file_url:
        tmp_file, tmp_abs_path = tempfile.mkstemp()
        tmp_file.close()
        Files.copy(file_url.openStream(), Paths.get(tmp_abs_path), StandardCopyOption.REPLACE_EXISTING)
        return tmp_abs_path
    else:
        return None

if 'REQUESTS_CA_BUNDLE' not in os.environ:
    set_ca_bundle_path()
