<?php
echo "Welcome~~~~~~~\n";
echo "###Test Case###: Security - Delete old files from tmp\n";
if(!empty($_GET["action"])) {
  $command1 = "touch -t 1001010101 /tmp/tmp_old 2>&1";
  echo "Command 1: ".$command1."\n";
  passthru($command1, $ret1);

  $command2 = "touch -t 1001010101 /var/tmp/var_tmp_old 2>&1";
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
  $command1 = "ls -l /tmp/tmp_old 2>&1 || ls -l /var/tmp/var_tmp_old 2>&1";
  echo "Command 1: ".$command1."\n";
  passthru($command1, $ret1); 

  $command = "ls -l /tmp 2>&1";
  echo "Command: ".$command."\n";
  passthru($command, $ret_tmp);

  if($ret1 == 0){
    echo "RESULT=0\n";
  } else {
    echo "RESULT=1\n";
  }
}
?>
