#!/bin/bash

# Install gcloud for mac
if [[ $1 == 'darwin' ]]
then
  if [[ $2 == 'x86_64' ]] # Intel 64 bit
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz -C ~/.cache/jina-now/
    rm google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz
    ~/.cache/jina-now/google-cloud-sdk/install.sh --quiet --install-python false
  elif [[ $2 == 'x86' ]] # 32 bit
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-x86.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-x86.tar.gz -C ~/.cache/jina-now/
    rm google-cloud-sdk-377.0.0-darwin-x86.tar.gz
    ~/.cache/jina-now/google-cloud-sdk/install.sh --quiet --install-python false
  else # M1 chip
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-arm.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-arm.tar.gz -C ~/.cache/jina-now/
    rm google-cloud-sdk-377.0.0-darwin-arm.tar.gz
    ~/.cache/jina-now/google-cloud-sdk/install.sh --quiet --install-python false
  fi
fi

# Install gcloud for linux
if [[ $1 == 'linux' ]]
then
  if [[ $2 == 'x86_64' ]] # Intel 64 bit
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-linux-x86_64.tar.gz
    tar -xf google-cloud-sdk-377.0.0-linux-x86_64.tar.gz -C ~/.cache/jina-now/
    rm google-cloud-sdk-377.0.0-linux-x86_64.tar.gz
    ~/.cache/jina-now/google-cloud-sdk/install.sh --quiet --install-python false
  elif [[ $2 == 'x86' ]] # 32 bit
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-linux-x86.tar.gz
    tar -xf google-cloud-sdk-377.0.0-linux-x86.tar.gz -C ~/.cache/jina-now/
    rm google-cloud-sdk-377.0.0-linux-x86.tar.gz
    ~/.cache/jina-now/google-cloud-sdk/install.sh --quiet --install-python false
  else # ARM chip
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-linux-arm.tar.gz
    tar -xf google-cloud-sdk-377.0.0-linux-arm.tar.gz -C ~/.cache/jina-now/
    rm google-cloud-sdk-377.0.0-linux-arm.tar.gz
    ~/.cache/jina-now/google-cloud-sdk/install.sh --quiet --install-python false
  fi
fi