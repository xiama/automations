<?php
echo "Welcome~~~~~~~\n";
if(!empty($_GET["action"])) {
  $action_name = $_GET["action"];
  if ($action_name == "create"){
    $con=mysql_connect($_ENV["OPENSHIFT_MYSQL_DB_HOST"].":".$_ENV["OPENSHIFT_MYSQL_DB_PORT"], $_ENV["OPENSHIFT_MYSQL_DB_USERNAME"], $_ENV["OPENSHIFT_MYSQL_DB_PASSWORD"]) or die(mysql_error());
    mysql_select_db($_ENV["OPENSHIFT_APP_NAME"],$con);
    mysql_query("DROP TABLE IF EXISTS ucctalk",$con);
    mysql_query("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))",$con);
    mysql_query("INSERT INTO ucctalk (speaker,title) VALUES ('speaker1', 'title1')",$con);
    $result=mysql_query("SELECT * FROM ucctalk",$con);
    while($row=mysql_fetch_array($result)) {
      echo $row['speaker'],", ",$row['title'],"\n";
    }
    mysql_close($con);
  } elseif ($action_name == "modify") {
    $con=mysql_connect($_ENV["OPENSHIFT_MYSQL_DB_HOST"].":".$_ENV["OPENSHIFT_MYSQL_DB_PORT"], $_ENV["OPENSHIFT_MYSQL_DB_USERNAME"], $_ENV["OPENSHIFT_MYSQL_DB_PASSWORD"]) or die(mysql_error());
    mysql_select_db($_ENV["OPENSHIFT_APP_NAME"],$con);
    mysql_query("DROP TABLE IF EXISTS ucctalk",$con);
    mysql_query("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))",$con);
    mysql_query("INSERT INTO ucctalk (speaker,title) VALUES ('speaker2', 'title2')",$con);
    $result=mysql_query("SELECT * FROM ucctalk",$con);
    while($row=mysql_fetch_array($result)) {
      echo $row['speaker'],", ",$row['title'],"\n";
    }
    mysql_close($con);
  } else {
    $con=mysql_connect($_ENV["OPENSHIFT_MYSQL_DB_HOST"].":".$_ENV["OPENSHIFT_MYSQL_DB_PORT"], $_ENV["OPENSHIFT_MYSQL_DB_USERNAME"], $_ENV["OPENSHIFT_MYSQL_DB_PASSWORD"]) or die(mysql_error());
    mysql_select_db($_ENV["OPENSHIFT_APP_NAME"],$con);
    $result=mysql_query("SELECT * FROM ucctalk",$con);
    while($row=mysql_fetch_array($result)) {
      echo $row['speaker'],", ",$row['title'],"\n";
    }
    mysql_close($con);
  }
} else {
    $con=mysql_connect($_ENV["OPENSHIFT_MYSQL_DB_HOST"].":".$_ENV["OPENSHIFT_MYSQL_DB_PORT"], $_ENV["OPENSHIFT_MYSQL_DB_USERNAME"], $_ENV["OPENSHIFT_MYSQL_DB_PASSWORD"]) or die(mysql_error());
    mysql_select_db($_ENV["OPENSHIFT_APP_NAME"],$con);
    $result=mysql_query("SELECT * FROM ucctalk",$con);
    while($row=mysql_fetch_array($result)) {
    echo $row['speaker'],", ",$row['title'],"\n";
  }
  mysql_close($con);
}
?>
