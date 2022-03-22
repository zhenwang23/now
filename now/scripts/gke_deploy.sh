#!/bin/bash

gcloud services enable container.googleapis.com --quiet
gcloud container clusters create $1 --quiet --machine-type e2-highmem-2 --num-nodes 1
gcloud container clusters get-credentials $1
