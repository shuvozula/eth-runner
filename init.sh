#!/bin/bash

# Provide the absolute path to the ethminer bin/ directory, eg: /etc/ethminer/bin/
ETHMINER_PATH=/usr/local/bin
export NO_COLOR=1

# ----------------------- Do not edit below this line --------------------------

my_dir="$(dirname $0)"
ACCOUNT_PATH="$my_dir/../.account"

if [ ! -d $ETHMINER_PATH ]; then
  echo "No ethminer found at ${ETHMINER_PATH}! Please install ethminer "
  exit 1
fi

if [ ! -f $ACCOUNT_PATH ]; then
  echo "ERROR: No .account file found!! Create one with just one line containing this: <account-hash>.<account-nickname>, in the root folder of this project"
  exit 1
else
  ACCOUNT=$(cat $ACCOUNT_PATH)
fi
