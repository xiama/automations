<?php
header("Content-Type: text/plain");
if(!empty($_GET["group"])) {
    $group = urldecode($_GET["group"]);
    if($group == "env") {
        foreach ($_ENV as $key=>$val) {
            echo $key."=".$val."\n";
        }
    }
}
else {
    echo "Usage: $_ENV[OPENSHIFT_APP_DNS]/universal.php?group=<group>\nnValid groups are 'shell', 'mongodb', 'mysql', 'postgresql'\n";
}
?>
