#!/bin/bash

docker build -t jina-now:0.0.1 .

docker run -it --rm \
--name jina-now \
--network="host" \
-v /var/run/docker.sock:/var/run/docker.sock \
-v $HOME/.kube:/root/.kube \
-v $PWD/jina-now:/root/data \
jina-now:0.0.1
