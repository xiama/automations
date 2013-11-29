<?php
echo "GEAR DNS: " . $_ENV["OPENSHIFT_GEAR_DNS"] . "<br />";
$con=mysql_connect($_ENV["OPENSHIFT_MYSQL_DB_HOST"].":".$_ENV["OPENSHIFT_MYSQL_DB_PORT"], $_ENV["OPENSHIFT_MYSQL_DB_USERNAME"], $_ENV["OPENSHIFT_MYSQL_DB_PASSWORD"]) or die(mysql_error());
mysql_select_db($_ENV["OPENSHIFT_APP_NAME"],$con);


mysql_query("DROP TABLE IF EXISTS ucctalk",$con);
mysql_query("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))",$con);
mysql_query("INSERT INTO ucctalk (speaker,title) VALUES ('Jeremy Zawodny', 'Optimizing MySQL'), ('Sanja Byelkin', 'Sub-Queries in MySQL'), ('Tim Bunce', 'Advanced Perl DBI')",$con);
$result=mysql_query("SELECT * FROM ucctalk",$con);
while($row=mysql_fetch_array($result))
{
echo $row['speaker'],", ",$row['title'],"<br />";
}
mysql_close($con);
?>
