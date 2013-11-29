<?php
echo "Gear DNS: ".$_ENV['OPENSHIFT_GEAR_DNS']."<br />";
#$m = new Mongo("mongodb://#user:#passwd@#host:#port");
#$db = $m->#dbname;

$m = new Mongo("mongodb://".$_ENV['OPENSHIFT_MONGODB_DB_USERNAME'].":".$_ENV['OPENSHIFT_MONGODB_DB_PASSWORD']."@".$_ENV['OPENSHIFT_MONGODB_DB_HOST'].":".$_ENV['OPENSHIFT_MONGODB_DB_PORT']);
$db = $m->$_ENV['OPENSHIFT_APP_NAME'];

if(!empty($_GET["action"])) {
    echo "MongoDB operations:<br />";
    if($_GET["action"] == "insert") {
        if(empty($_GET["size"])) {
            $size = 500000;
        }
        else {
            $size = (int)$_GET["size"];
        }
        echo "db.data.insert({data: \"This is testing data for testing snapshoting and restoring big data in mongodb database.This is testing data for testing snapshoting and restoring big data in mongodb database.\"})<br />";
        for($i = 0; $i < $size; $i++) {
            $db->info->insert(array("data" => "This is testing data for testing snapshoting and restoring big data in mongodb database.This is testing data for testing snapshoting and restoring big data in mongodb database."));
        }
        echo (string)$size." records have been inserted into mongodb<br />";
    }
    elseif($_GET["action"] == "delete") {
        echo "db.info.remove()<br />";
        $db->info->remove();
        echo "All the records have been deleted from mongodb database<br />";
    }
    elseif($_GET["action"] == "show") {
        $cursor = $db->info->find();
        $num = $cursor->count();
        if($num > 0) {
            echo "There are ".$num." records in database<br />Here's one record: ";
            $obj = $cursor->getNext();
            echo $obj["data"]."<br />";
        }
        else {
            echo "There is no record in database<br />";
        }
    }
    else {
        echo "[US2103][RT]Alter domain for a scaling php app which having mongodb added<br />";
    }
}
?>
