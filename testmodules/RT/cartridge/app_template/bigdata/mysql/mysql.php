<?php
$con=mysql_connect($_ENV["OPENSHIFT_MYSQL_DB_HOST"].":".$_ENV["OPENSHIFT_MYSQL_DB_PORT"], $_ENV["OPENSHIFT_MYSQL_DB_USERNAME"], $_ENV["OPENSHIFT_MYSQL_DB_PASSWORD"]) or die(mysql_error());
mysql_select_db($_ENV["OPENSHIFT_APP_NAME"],$con);
mysql_query("CREATE TABLE IF NOT EXISTS info(id INT NOT NULL AUTO_INCREMENT, data CHAR(200), PRIMARY KEY (id));", $con);
mysql_query("COMMIT", $con);
if(!empty($_GET["action"])) {
    if($_GET["action"] == "insert") {
        echo "Gear DNS: ".$_ENV['OPENSHIFT_GEAR_DNS']."<br />";
        echo "SQL statements:<br />";
        echo "INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');<br /><br />";
        if(empty($_GET["size"])) {
            $size = 500000;
        }
        else {
            $size = (int)$_GET["size"];
        }
        mysql_query("SET autocommit=0;");
        for($i = 0; $i < $size; $i++) {
            mysql_query("INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');", $con);
        }
        mysql_query("COMMIT;");
        mysql_query("SET autocommit=1;");
        echo (string)$size." records have been inserted into mysql";
    }
    elseif($_GET["action"] == "delete") {
        echo "Gear DNS: ".$_ENV['OPENSHIFT_GEAR_DNS']."<br />";
        echo "SQL statement: DELETE FROM info;<br />";
        mysql_query("DELETE FROM info;", $con);
        echo "All the records have been deleted from mysql database";
    }
    elseif($_GET["action"] == "show") {
        echo "Gear DNS: ".$_ENV['OPENSHIFT_GEAR_DNS']."<br />";
        echo "SQL statement: SELECT * from info;<br />";
        $result = mysql_query("SELECT * from info;", $con);
        $num = mysql_num_rows($result);
        if($num > 0) {
            echo "There are ".$num." records in database<br />Here's one row:";
            $row = mysql_fetch_array($result);
            echo $row['id'],", ",$row['data'],"<br />";
        }
        else {
            echo "There is no record in database<br />";
        }
    }
    else {
        echo "[rhc-cartridge]snapshot/restore big mysql data to existing app<br />[rhc-cartridge]snapshot/restore big mysql data to new app<br />";
    }
}
mysql_query("COMMIT", $con);
mysql_close($con);
?>
