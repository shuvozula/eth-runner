#!/bin/bash

my_dir="$(dirname $0)"

ETHMINER_PATH=/home/shuvo/.ethminer/bin
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