#!/bin/bash

VERSION='1.0.0rc5'

docker build . -t fredericklab/picachooser:${VERSION}
docker build . -t fredericklab/picachooser:latest
docker push fredericklab/picachooser:1${VERSION}
docker push fredericklab/picachooser:latest
docker pull fredericklab/picachooser:1${VERSION}
