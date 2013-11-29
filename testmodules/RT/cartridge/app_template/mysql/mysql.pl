#!/usr/bin/perl
print "Content-type: text/plain\r\n\r\n";
use DBI;
my $dbname = $ENV{'OPENSHIFT_APP_NAME'};
my $location = $ENV{'OPENSHIFT_MYSQL_DB_HOST'};
my $port = $ENV{'OPENSHIFT_MYSQL_DB_PORT'};
my $database = "DBI:mysql:$dbname:$location:$port";
my $db_user = $ENV{'OPENSHIFT_MYSQL_DB_USERNAME'};
my $db_pass = $ENV{'OPENSHIFT_MYSQL_DB_PASSWORD'};
my $dbh = DBI->connect($database,$db_user,$db_pass) or die "Cannot connect database";


my $sth = $dbh->prepare("DROP TABLE IF EXISTS ucctalk") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("INSERT INTO ucctalk (speaker,title) VALUES ('Jeremy Zawodny', 'Optimizing MySQL'), ('Sanja Byelkin', 'Sub-Queries in MySQL'), ('Tim Bunce', 'Advanced Perl DBI')") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("SELECT * FROM ucctalk") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
print "GEAR DNS: " + $ENV{"OPENSHIFT_GEAR_DNS"} + "<br />";
while (@ary = $sth->fetchrow_array())
{
    print join(", ",@ary),"\n";
}
$sth->finish();
$dbh->disconnect;
