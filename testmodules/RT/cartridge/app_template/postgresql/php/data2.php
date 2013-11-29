<?php
header('Content-Type: text/plain');
$con = pg_connect("dbname=".$_ENV["OPENSHIFT_APP_NAME"]." "."user=".$_ENV["OPENSHIFT_POSTGRESQL_DB_USERNAME"]." "."password=".$_ENV["OPENSHIFT_POSTGRESQL_DB_PASSWORD"]." "."host=".$_ENV["OPENSHIFT_POSTGRESQL_DB_HOST"]." "."port=".$_ENV["OPENSHIFT_POSTGRESQL_DB_PORT"]) or die('Could not connect to the database: ' + pg_last_error());

pg_query($con, "DROP TABLE IF EXISTS info;");
pg_query($con, "CREATE TABLE info(id integer PRIMARY KEY, data text);");
pg_query($con, "INSERT INTO info VALUES(1, '#str_random2#');");
pg_close($con);
echo "Please visit /show.php to see the data";
?>
