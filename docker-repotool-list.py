#!/usr/bin/env python
#

import requests
from requests.auth import HTTPBasicAuth
import sys
import os
from datetime import datetime

class CommunicationException(Exception):
    def __init__(self, message):
        self.message = message

docker_url = os.environ.get('URL', None)
credentials_login = os.environ.get('USER', None)
credentials_password = os.environ.get('PASSWORD', None)

credentials = HTTPBasicAuth(credentials_login, credentials_password)
getRepositoryCatalogUrl = "%s/v2/_catalog" % docker_url
getRepositoryCatalogResponse = requests.get(getRepositoryCatalogUrl, auth = credentials)
if getRepositoryCatalogResponse.status_code != 200:
    raise CommunicationException("Unexpected response status code: %s" % getRepositoryCatalogResponse.status_code)
getRepositoryCatalogResponseList = getRepositoryCatalogResponse.json()

for path in getRepositoryCatalogResponseList['repositories']:
    getRepositorySnapshotsUrl = "%s/v2/%s/tags/list" % (docker_url, path)
    getRepositorySnapshotsResponse = requests.get(getRepositorySnapshotsUrl, auth = credentials)
    if getRepositorySnapshotsResponse.status_code != 200:
        raise CommunicationException("Unexpected response status code: %s" % getRepositorySnapshotsResponse.status_code)
    getRepositorySnapshotsResponseList = getRepositorySnapshotsResponse.json()

    for snapshot_key in getRepositorySnapshotsResponseList['tags']:
        getSnapshotsInfoUrl = '%s/v2/%s/manifests/%s' % (docker_url, path, snapshot_key)
        getSnapshotsInfoResponse = requests.head(getSnapshotsInfoUrl, auth = credentials, headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'})
        if getSnapshotsInfoResponse.status_code != 200:
            raise CommunicationException("Unexpected response status code: %s" % getSnapshotsInfoResponse.status_code)
        #getSnapshotsInfo = getSnapshotsInfoResponse.json() DELETE
        #inner_json_v1_compatibility_str = getSnapshotsInfo['history'][0]['v1Compatibility'] DELETE
        #inner_json_v1_compatibility = json.loads(inner_json_v1_compatibility_str) DELETE
        #created = inner_json_v1_compatibility['created'] DELETE
        snapshot_last_modified = getSnapshotsInfoResponse.headers['Last-Modified']
        snapshot_last_modified_converted = datetime.strptime(snapshot_last_modified, "%a, %d %b %Y %X %Z").strftime("%Y-%m-%dT%H:%M:%SZ")
        docker_digest_content = getSnapshotsInfoResponse.headers['Docker-Content-Digest']
        print("%s:%s %s %s" % (path, snapshot_key, snapshot_last_modified_converted, docker_digest_content))
        sys.stdout.flush()
