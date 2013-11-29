<?php
if(!empty($_GET["action"])) {
    if(empty($_GET["size"])) {
        $size = "300";
    }
    else {
        $size = $_GET["size"];
    }
    if($_GET["action"] == "create") {
        $cmd = "dd if=/dev/urandom of=".$_ENV['OPENSHIFT_DATA_DIR']."bigfile bs=1M count=".$size;
        $output = system($cmd, $ret);
        echo "Command: ".$cmd."<br />";
        if($ret == 0) {
            echo "The bigfile has been created.<br />";
        }
        else {
            echo "Failed to create bigfile under OPENSHIFT_DATA_DIR";
        }
    }
    elseif($_GET["action"] == "delete") {
        $cmd = "rm -f ".$_ENV['OPENSHIFT_DATA_DIR']."bigfile";
        $output = system($cmd, $ret);
        echo "The bigfile has been deleted.";
    }
    elseif($_GET["action"] == "show") {
        $filepath = $_ENV['OPENSHIFT_DATA_DIR']."bigfile";
        $cmd = "ls -lh ".$filepath;
        echo "Command: ".$cmd."\n";
        $output = system($cmd, $ret);
        if(file_exists($filepath)) {
            echo "<br />".$output;
            echo "<br />The bigfile exists.";
        }
        else {
            echo "<br />The bigfile doesnot exist.";
        }
    }
}
?>
