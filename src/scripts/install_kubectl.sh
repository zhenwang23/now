#!/bin/bash

# Install kubectl
if [[ $1 == 'darwin' ]]
then
  if [[ $2 == 'x86_64' ]]
  then
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl.sha256"
    echo "$(<kubectl.sha256)  kubectl" | shasum -a 256 --check
    chmod +x ./kubectl
    mv ./kubectl /usr/local/bin/kubectl
  else
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl.sha256"
    echo "$(<kubectl.sha256)  kubectl" | shasum -a 256 --check
    chmod +x ./kubectl
    mv ./kubectl /usr/local/bin/kubectl
  fi
fi

if [[ $1 == 'linux' ]]
then
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
  echo "$(<kubectl.sha256)  kubectl" | sha256sum --check
  chmod +x kubectl
  mkdir -p ~/.local/bin/kubectl
  mv ./kubectl ~/.local/bin/kubectl
  echo 'export PATH=$PATH:~/.local/bin'  >> ~/.bash_profile
  #  mv ./kubectl /usr/local/bin/kubectl
fi