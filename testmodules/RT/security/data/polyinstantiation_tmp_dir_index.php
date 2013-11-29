<?php
echo "Welcome~~~~~~~\n";
echo "###Test Case###: Security - Polyinstantiation of /tmp and /var/tmp for new application by using pam_namespace\n";
if(!empty($_GET["action"])) {
  $command1 = "touch /tmp/php_tmp_test 2>&1";
  echo "Command 1: ".$command1."\n";
  passthru($command1, $ret1);

  $command2 = "touch /var/tmp/php_var_tmp_test 2>&1";
  echo "Command 2: ".$command2."\n";
  passthru($command2, $ret2);

  $command = "ls -l /tmp 2>&1";
  echo "Command: ".$command."\n";
  passthru($command, $ret_tmp);

  if($ret1 == 0 && $ret2 == 0){
    echo "RESULT=0\n";
  } else {
    echo "RESULT=1\n";
  }
} else {
  $command1 = "ls -l /tmp/php_tmp_test 2>&1 && ls -l /var/tmp/php_var_tmp_test 2>&1";
  echo "Command 1: ".$command1."\n";
  passthru($command1, $ret1); 

  $command = "ls -l /tmp/ 2>&1";
  echo "Command: ".$command."\n";
  passthru($command, $ret_tmp);

  if($ret1 == 0){
    echo "RESULT=0\n";
  } else {
    echo "RESULT=1\n";
  }
}
?>
