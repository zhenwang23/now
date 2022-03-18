#!/bin/bash

# Install gcloud for mac
if [[ $1 == 'darwin' ]]
then
  if [[ $2 == 'x86_64' ]] # Intel 64 bit
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz && rm google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz
    ./google-cloud-sdk/install.sh -q
  elif [[ $2 == 'x86' ]] # 32 bit
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-x86.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-x86.tar.gz && rm google-cloud-sdk-377.0.0-darwin-x86.tar.gz
    ./google-cloud-sdk/install.sh -q
  else # M1 chip
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-arm.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-arm.tar.gz&& rm google-cloud-sdk-377.0.0-darwin-arm.tar.gz
    ./google-cloud-sdk/install.sh -q
  fi
fi

# Install gcloud for linux
if [[ $1 == 'linux' ]]
then
  if [[ $2 == 'x86_64' ]] # Intel 64 bit
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-linux-x86_64.tar.gz
    tar -xf google-cloud-sdk-377.0.0-linux-x86_64.tar.gz && rm google-cloud-sdk-377.0.0-linux-x86_64.tar.gz
    ./google-cloud-sdk/install.sh -q
  elif [[ $2 == 'x86' ]] # 32 bit
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-linux-x86.tar.gz
    tar -xf google-cloud-sdk-377.0.0-linux-x86.tar.gz && rm google-cloud-sdk-377.0.0-linux-x86.tar.gz
    ./google-cloud-sdk/install.sh -q
  else # ARM chip
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-linux-arm.tar.gz
    tar -xf google-cloud-sdk-377.0.0-linux-arm.tar.gz&& rm google-cloud-sdk-377.0.0-linux-arm.tar.gz
    ./google-cloud-sdk/install.sh -q
  fi