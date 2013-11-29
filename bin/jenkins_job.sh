#!/bin/bash

#  File name: jenkins_job.sh
#  Date:      2012/10/04 09:31
#  Author:    mzimen@redhat.com

####################################
### checking mandatory variables ###
####################################
test -z "$JENKINS_JOB_TOKEN" && { echo "ERROR: Missing JENKINS_JOB_TOKEN variable"; exit 1; } 
test -z "$TCMS_USER" && { echo "ERROR: Missing TCMS_USER variable"; exit 1; } 
test -z "$TCMS_PASSWORD" && { echo "ERROR: Missing TCMS_PASSWORD variable"; exit 1; } 


#### SET THE ENVIRONMENT VARIABLES AS NEEDED
export RHTEST_HOME=$(pwd)
export PATH=${RHTEST_HOME}/bin:${RHTEST_HOME}/lib:${RHTEST_HOME}/lib/supports:${RHTEST_HOME}/testmodules:$PATH
export PYTHONPATH=${RHTEST_HOME}/bin:${RHTEST_HOME}/lib:${RHTEST_HOME}/lib/supports:${RHTEST_HOME}/testmodules:$PYTHONPATH


#### THIS WILL AUTHENTICATE TO NITRATE

echo -e "\nDEBUG: Kerberos init..."
kinit.sh || exit 1


test -n "$AMI_ID" && OPTIONS="${OPTIONS} -m $AMI_ID -z t1.micro "
test -n "$TESTRUN_ID" && OPTIONS="${OPTIONS} -i $TESTRUN_ID "
test -n "$INSTANCE_IP" && OPTIONS="${OPTIONS} -a $INSTANCE_IP "
test -n "$TESTRUN_TAG" && OPTIONS="${OPTIONS} -t $TESTRUN_TAG "
test -n "$TCMS_TAGS" && OPTIONS="${OPTIONS} -g $TCMS_TAGS "


if [ "$SLAVE" == "false" ]; then
  echo "##########################################################"
  echo "MASTER..."
  echo "##########################################################"

  test -z "$POOL_ACCOUNT" && { echo "ERROR: Missing POOL_ACCOUNT variable"; exit 1; } 

  #WHERE TO RUN...
  if [ -n "$INSTANCE_IP" ]; then
    WHERE="{ \"name\": \"INSTANCE_IP\", \"value\": \"$INSTANCE_IP\" }, "
  else
    WHERE="{ \"name\": \"AMI_ID\", \"value\": \"$AMI_ID\" }, "
  fi

  if [ -z "$TESTRUN_ID" ]; then
    if [ -z "$TCMS_TAGS" ]; then
        echo "ERROR: Missing TCMS_TAGS argument, when no TESTRUN_ID was defined"
        exit 1
    fi
    echo -e "\nDEBUG: Creating new testrun..."
    TESTRUN_ID=$(create_test_run.py -t $TESTRUN_TAG -g $TCMS_TAGS | awk -F ':' '/test_run/{print $2}')
    if [ -z "$TESTRUN_ID" ]; then
        echo "ERROR: Unable to create testrun"
        exit 1
    fi
    echo "DEBUG: testrun_id=$TESTRUN_ID"
  else
    if [ "$RESET_TESTRUN" == "true" ]; then
      echo -e "\nDEBUG: Resetting testrun..."
      python $RHTEST_HOME/bin/reset_testrun.py $TESTRUN_ID
      if [ -n "$TCMS_TAGS" ]; then
        echo "DEBUG: Refresing testrun with $TCMS_TAGS"
        python $RHTEST_HOME/bin/refresh_testrun_by_tag.py $TESTRUN_ID $TCMS_TAGS
      fi
    fi
  fi

#
# Each slave can run ONLY with TESTRUN_ID !
#
  for acc in $POOL_ACCOUNT; do
    OPENSHIFT_user_email=$(echo $acc | awk -F ":" '{print $1}')
    OPENSHIFT_user_passwd=$(echo $acc | awk -F ":" '{print $2}')
  
 
    json="{ \"parameter\": [ 
$WHERE
{ \"name\": \"TESTRUN_ID\", \"value\": \"$TESTRUN_ID\" },
{ \"name\": \"OPENSHIFT_user_passwd\", \"value\":\"$OPENSHIFT_user_passwd\"}, 
{ \"name\": \"OPENSHIFT_user_email\", \"value\":\"$OPENSHIFT_user_email\"}, 
{ \"name\": \"SLAVE\", \"value\":\"true\" },
{ \"name\": \"TCMS_USER\", \"value\" : \"$TCMS_USER\"},
{ \"name\": \"TCMS_PASSWORD\", \"value\":\"$TCMS_PASSWORD\" } ]}"

    JENKINS_URL="http://ciqe.englab.nay.redhat.com"
    DELAY=$((DELAY+20))
    URL="$JENKINS_URL/job/$JOB_NAME/build?token=$JENKINS_JOB_TOKEN&delay=$DELAY"
  
    curl -s -L -k -X POST -H "Accept:application/json" -u mzimen:redhat -d token=devenv $URL --data-urlencode json="$json"  | elinks -dump |head
    echo -e "\n****************************************************************\n"

  done
else
###############################################################################
###############################################################################
###############################################################################
  echo -e "\nSLAVE\n"
  #this might have influen
  echo "DEBUG: Updating the client..."
  if [ -n "$CLIENT_VERSION" ]; then
      python $RHTEST_HOME/bin/update_rhc_client.py --release $CLIENT_VERSION
  else
      python $RHTEST_HOME/bin/update_rhc_client.py 
  fi

  echo -e "\nDEBUG: Launching the testrun...\n"

  python $RHTEST_HOME/bin/launcher.py $OPTIONS
  if [ -n "$SHUTDOWN" ]; then
      if [ -n "$INSTANCE_NAME" ]; then
          echo "ERROR: Missing INSTANCE_NAME for shutdown the instance"
      else
          python $RHTEST_HOME/bin/shutdow_instance.py -i $INSTANCE_NAME
      fi
  fi
fi

exit 0

#### END
