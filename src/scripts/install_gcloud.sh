#!/bin/bash

# Install gcloud for mac
if [[ $1 == 'darwin' ]]
then
  if [[ $2 == 'x86_64' ]]
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz && rm google-cloud-sdk-377.0.0-darwin-x86_64.tar.gz
    ./google-cloud-sdk/install.sh -q
  elif [[ $2 == 'x86' ]]
  then
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-x86.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-x86.tar.gz && rm google-cloud-sdk-377.0.0-darwin-x86.tar.gz
    ./google-cloud-sdk/install.sh -q
  else
    curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-377.0.0-darwin-arm.tar.gz
    tar -xf google-cloud-sdk-377.0.0-darwin-arm.tar.gz&& rm google-cloud-sdk-377.0.0-darwin-arm.tar.gz
    ./google-cloud-sdk/install.sh -q
  fi
fi