#!/usr/bin/env bash

set -ex

rm -rf _build && make clean

make dirhtml
