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

docker_registry_control_url = os.environ.get('DOCKER_REGISTRY_CONTROL_URL', None)
docker_registry_control_user = os.environ.get('DOCKER_REGISTRY_CONTROL_USER', None)
docker_registry_control_password = os.environ.get('DOCKER_REGISTRY_CONTROL_PASSWORD', None)

if docker_registry_control_url is None:
    print("A required environment variable 'DOCKER_REGISTRY_CONTROL_URL' is not set. Your have to provide your Docker URL in the variable")
    sys.exit(1)
elif docker_registry_control_user is None:
    print("A required environment variable 'DOCKER_REGISTRY_CONTROL_USER' is not set. Your have to provide your User Login in the variable")
    sys.exit(1)
elif docker_registry_control_password is None:
    print("A required environment variable 'DOCKER_REGISTRY_CONTROL_PASSWORD' is not set. Your have to provide your User Password in the variable")
    sys.exit(1)
else:
    credentials = HTTPBasicAuth(docker_registry_control_user, docker_registry_control_password)
    getRepositoryCatalogUrl = "%s/v2/_catalog" % docker_registry_control_url
    getRepositoryCatalogResponse = requests.get(getRepositoryCatalogUrl, auth = credentials)
    if getRepositoryCatalogResponse.status_code != 200:
        raise CommunicationException("Unexpected response status code: %s" % getRepositoryCatalogResponse.status_code)
    getRepositoryCatalogResponseList = getRepositoryCatalogResponse.json()

    for path in getRepositoryCatalogResponseList['repositories']:
        getRepositorySnapshotsUrl = "%s/v2/%s/tags/list" % (docker_registry_control_url, path)
        getRepositorySnapshotsResponse = requests.get(getRepositorySnapshotsUrl, auth = credentials)
        if getRepositorySnapshotsResponse.status_code != 200:
            raise CommunicationException("Unexpected response status code: %s" % getRepositorySnapshotsResponse.status_code)
        getRepositorySnapshotsResponseList = getRepositorySnapshotsResponse.json()

        for snapshot_key in getRepositorySnapshotsResponseList['tags']:
            getSnapshotsInfoUrl = '%s/v2/%s/manifests/%s' % (docker_registry_control_url, path, snapshot_key)
            getSnapshotsInfoResponse = requests.head(getSnapshotsInfoUrl, auth = credentials, headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'})
            if getSnapshotsInfoResponse.status_code != 200:
                raise CommunicationException("Unexpected response status code: %s" % getSnapshotsInfoResponse.status_code)
            snapshot_last_modified = getSnapshotsInfoResponse.headers['Last-Modified']
            snapshot_last_modified_converted = datetime.strptime(snapshot_last_modified, "%a, %d %b %Y %X %Z").strftime("%Y-%m-%dT%H:%M:%SZ")
            docker_digest_content = getSnapshotsInfoResponse.headers['Docker-Content-Digest']
            print("%s:%s %s %s" % (path, snapshot_key, snapshot_last_modified_converted, docker_digest_content))
            sys.stdout.flush()
