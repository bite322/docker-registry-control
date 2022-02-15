# Docker Registry List

*Docker Registry Control* is a application used for check last modified date and digest content of repository files.

## Quick Start

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install --requirement requirements.txt
```

## Launch

```shell
export DOCKER_REGISTRY_CONTROL_URL="url"
export DOCKER_REGISTRY_CONTROL_USER="login"
export DOCKER_REGISTRY_CONTROL_PASSWORD="xxxxxxxx"
./drctl-list.py | tee result.txt
```
