<?php
echo "Welcome~~~~~~~\n";
$target_file = $_ENV['OPENSHIFT_DATA_DIR']."php_data_test";

if(!empty($_GET["action"])) {
  $action_name = $_GET["action"];
  if ($action_name == "create"){
    $key_string = "snapshot_restore_data_dir_test1";
    $command1 = "echo ".$key_string." >".$target_file." 2>&1";
    echo "Command 1: ".$command1."\n";
    passthru($command1, $ret1);
    $command2 = "dd if=/dev/urandom of=".$_ENV['OPENSHIFT_DATA_DIR']."bigfile bs=1M count=1";
    echo "Command 2: ".$command2."\n";
    passthru($command2, $ret2);

    $command = "cat ".$target_file." 2>&1 && [ -f ".$_ENV['OPENSHIFT_DATA_DIR']."bigfile ]";
    echo "Command: ".$command."\n";
    passthru($command, $ret_tmp);

    if($ret1 == 0 and $ret2 == 0 and $ret_tmp == 0){
      echo "RESULT=0\n";
    } else {
      echo "RESULT=1\n";
    }
  } elseif ($action_name == "modify") {
    $key_string = "snapshot_restore_data_dir_test2";
    $command1 = "echo ".$key_string." >".$target_file." 2>&1";
    echo "Command 1: ".$command1."\n";
    passthru($command1, $ret1);
    $command2 = "rm -f ".$_ENV['OPENSHIFT_DATA_DIR']."bigfile";
    echo "Command 2: ".$command2."\n";
    passthru($command2, $ret2);

    $command = "cat ".$target_file." 2>&1 && [ ! -f ".$_ENV['OPENSHIFT_DATA_DIR']."bigfile ]";
    echo "Command: ".$command."\n";
    passthru($command, $ret_tmp);

    if($ret1 == 0 and $ret2 == 0 and $ret_tmp == 0){
      echo "RESULT=0\n";
    } else {
      echo "RESULT=1\n";
    }
  } else {
    $command = "cat ".$target_file." 2>&1";
    echo "Command: ".$command."\n";
    passthru($command, $ret_tmp);
    $command2 = "[ -f ".$_ENV['OPENSHIFT_DATA_DIR']."bigfile ]";
    echo "Command: ".$command2."\n";
    passthru($command2, $ret2);
    if ($ret2 == 0) {
        echo "file: bigfile exists\n";
    }
    else {
        echo "file: bigfile doesn't exist\n";
    }
  }
} else {
  $command = "cat ".$target_file." 2>&1";
  echo "Command: ".$command."\n";
  passthru($command, $ret_tmp);
  $command2 = "[ -f ".$_ENV['OPENSHIFT_DATA_DIR']."bigfile ]";
  echo "Command: ".$command2."\n";
  passthru($command2, $ret2);
  if ($ret2 == 0) {
    echo "file: bigfile exists\n";
  }
  else {
    echo "file: bigfile does not exist\n";
  }
}

?>
