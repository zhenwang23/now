#!/bin/bash

$2 services enable container.googleapis.com --quiet
$2 container clusters create $1 --quiet --machine-type e2-highmem-2 --num-nodes 1
$2 container clusters get-credentials $1
