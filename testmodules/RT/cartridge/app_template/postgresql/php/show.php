<?php
header('Content-Type: text/plain');
$db = pg_connect("dbname=".$_ENV["OPENSHIFT_APP_NAME"]." "."user=".$_ENV["OPENSHIFT_POSTGRESQL_DB_USERNAME"]." "."password=".$_ENV["OPENSHIFT_POSTGRESQL_DB_PASSWORD"]." "."host=".$_ENV["OPENSHIFT_POSTGRESQL_DB_HOST"]." "."port=".$_ENV["OPENSHIFT_POSTGRESQL_DB_PORT"]) or die('Could not connect to the database: ' + pg_last_error());

$result=pg_query("SELECT data FROM info;");

while( $row = pg_fetch_array($result) ) {
    echo $row[0];
}
pg_close($db);
?>
