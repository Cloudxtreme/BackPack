#!/bin/bash

# make sure that pass.txt is in your root
# directory

if [ -d $1 ]; then
	cd $1
fi

bcrypt *.* < /pass.txt
