#!/bin/sh

#
# Variables below might be obtained from Jenkins job parameters
#
if [ -f $RHTEST_HOME/bin/kinit.expect ]; then
    $RHTEST_HOME/bin/kinit.expect "$TCMS_USER" "$TCMS_PASSWORD"
elif [ -f ./kinit.expect ]; then 
    ./kinit.expect "$TCMS_USER" "$TCMS_PASSWORD"
else
    echo "Unable to find 'kinit.expect' file"
    exit 3
fi
