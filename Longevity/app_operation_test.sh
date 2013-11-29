#!/bin/bash
. ./function.sh
app_operations="status start restart reload stop force-stop tidy delete"
run app_oper_testing $1
