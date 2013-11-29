#!/usr/bin/perl
print "Content-type: text/plain\r\n\r\n";
use DBI;
#my $dbname = "#pgsql_dbname#";
#my $host = "#pgsql_host#";
#my $port = "#pgsql_port#";
my $dbname = $ENV{'OPENSHIFT_APP_NAME'};
my $host = $ENV{'OPENSHIFT_POSTGRESQL_DB_HOST'};
my $port = $ENV{'OPENSHIFT_POSTGRESQL_DB_PORT'};

my $database = "dbi:Pg:dbname=$dbname;host=$host;port=$port";
#my $db_user = "#pgsql_user#";
#my $db_pass = "#pgsql_passwd#";
my $db_user = $ENV{'OPENSHIFT_POSTGRESQL_DB_USERNAME'};
my $db_pass = $ENV{'OPENSHIFT_POSTGRESQL_DB_PASSWORD'};

my $dbh = DBI->connect($database,$db_user,$db_pass,{AutoCommit => 1}) or die "Cannot connect database";

my $sth = $dbh->prepare("DROP TABLE IF EXISTS info;") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("CREATE TABLE info(id integer PRIMARY KEY, data text);") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("INSERT INTO info VALUES(1, '#str_random1#');") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
print "Please visit /show.pl to see the data\n";
$sth->finish();
$dbh->disconnect;
