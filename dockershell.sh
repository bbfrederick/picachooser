#!/bin/bash

VERSION=latest

docker pull fredericklab/picachooser:${VERSION}
docker run -it fredericklab/picachooser:${VERSION} xyzzy
