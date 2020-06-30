#!/bin/bash

VERSION='1.0.1'

docker build . -t fredericklab/picachooser:${VERSION}
docker build . -t fredericklab/picachooser:latest
docker push fredericklab/picachooser:${VERSION}
docker push fredericklab/picachooser:latest
docker pull fredericklab/picachooser:${VERSION}
docker pull fredericklab/picachooser:latest
