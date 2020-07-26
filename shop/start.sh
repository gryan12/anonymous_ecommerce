#!/bin/bash

export AGENT_NAME=$1

shift
if  [[ $AGENT_NAME =~ "flask" ]]
then
	echo "flask agent: {$AGENT_NAME}"	
	python -m shop.runners.flaskcontroller $@
else
	python -m shop.runners.$AGENT_NAME $@
fi
