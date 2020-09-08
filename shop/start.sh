#!/bin/bash
export AGENT_NAME=$1
echo "flask agent: {$AGENT_NAME}"
python -m shop.src.app $@
