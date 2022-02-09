#!/usr/bin/env python
#

import requests
from requests.auth import HTTPBasicAuth
import sys
import os

class CommunicationException(Exception):
    def __init__(self, message):
        self.message = message

dockerUrl = os.environ.get('URL', None)
credentialsLogin = os.environ.get('USER', None)
credentialsPassword = os.environ.get('PASSWORD', None)

credentials = HTTPBasicAuth(credentialsLogin, credentialsPassword)
getRepositoryCatalog = "%s/v2/_catalog" % dockerUrl
getRepositoryCatalogResponse = requests.get(getRepositoryCatalog, auth = credentials)
if getRepositoryCatalogResponse.status_code != 200:
    raise CommunicationException("Unexpected response status code: %s" % getRepositoryCatalogResponse.status_code)
getRepositoryCatalogResponseList = getRepositoryCatalogResponse.json()

for path in getRepositoryCatalogResponseList['repositories']:
    pathSplit = path.split('/')
    pathq = pathSplit[-1]
    getRepositoryUrl = "%s/v2/%s/tags/list" % (dockerUrl, path)
    getRepositorySnapshotResponse = requests.get(getRepositoryUrl, auth = credentials)
    if getRepositorySnapshotResponse.status_code != 200:
        raise CommunicationException("Unexpected response status code: %s" % getRepositorySnapshotResponse.status_code)
    getRepositorySnapshotResponseList = getRepositorySnapshotResponse.json()

    for key in getRepositorySnapshotResponseList['tags']:
        getSnapshotsInfoUrl = '%s/v2/%s/manifests/%s' % (dockerUrl, path, key)
        getSnapshotsInfoResponse = requests.get(getSnapshotsInfoUrl, auth = credentials)
        if getSnapshotsInfoResponse.status_code != 200:
            raise CommunicationException("Unexpected response status code: %s" % getSnapshotsInfoResponse.status_code)
        getSnapshotsInfo = getSnapshotsInfoResponse.json()
        getSnapshotsInfoList = getSnapshotsInfo['history'][0]['v1Compatibility'].split('"')
        date = getSnapshotsInfoList[3]
        print("%s/%s %s" % (path, key, date))
        sys.stdout.flush()
