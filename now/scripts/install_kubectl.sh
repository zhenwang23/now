#!/bin/bash

# Install kubectl
if [[ $1 == 'darwin' ]]
then
  if [[ $2 == 'x86_64' ]]
  then
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
    chmod +x ./kubectl
    mkdir -p ~/.cache/jina-now
    mv ./kubectl ~/.cache/jina-now/kubectl
  else
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"
    chmod +x ./kubectl
    mkdir -p ~/.cache/jina-now
    mv ./kubectl ~/.cache/jina-now/kubectl
  fi
fi

if [[ $1 == 'linux' ]]
then
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl
  mkdir -p ~/.cache/jina-now
  mv ./kubectl ~/.cache/jina-now/kubectl
fi