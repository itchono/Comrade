#!/bin/bash

QUERY=`curl https://api.github.com/repos/itchono/Comrade/actions/runs 2> /dev/null`

update_deploy () {
  local BRANCH=$1
  local UPDATE_FILE=$2
  
  # status completed and conclusion success and right branch
  local COMMIT=`echo $QUERY | jq --arg branch "$BRANCH" -r '[.workflow_runs[] | select((.status == "completed") and (.conclusion == "success") and (.head_branch == $branch)).head_sha][0]'`
  if [ ${#COMMIT} == 40 ]
  then
  
    local TAG="sha-${COMMIT:0:7}"
    echo "Tag: $TAG"
  
    local DIR="$(cd "$(dirname "$0")" && pwd)"
    local FILE="$DIR/${BRANCH}_COMMIT"
  
    if [ ! -f $FILE ]
    then
      echo "default" > $FILE
    fi
  
    local COMRADE_COMMIT=$(cat "$FILE")
    
    if [ "$COMMIT" != "$COMRADE_COMMIT" ]
    then
      echo "Updating $BRANCH image."
      echo $COMMIT > $FILE
    
      local KUBE_FILE=$DIR/$UPDATE_FILE
    
      sed -i "s/\\(itchono\/comrade:\\).*/\\1$TAG/" "$KUBE_FILE"
      kubectl apply -f $KUBE_FILE
    fi
  else
    echo "Query error"
  fi
}

update_deploy "master" "v2/deploy.yaml"
update_deploy "Comrade-V3-dev" "v3/deploy.yaml"

