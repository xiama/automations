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


my $sth = $dbh->prepare("CREATE TABLE IF NOT EXISTS info(id INT NOT NULL AUTO_INCREMENT, data CHAR(200), PRIMARY KEY (id));") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("COMMIT;") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";

# Get query string
my $in = {};
$in{'action'} = '';
$in{'size'} = '';
if(length($ENV{'QUERY_STRING'}) > 0) {
    $buffer = $ENV{'QUERY_STRING'};
    @pairs = split(/&/, $buffer);
    foreach $pair (@pairs){
        ($name, $value) = split(/=/, $pair);
        $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
        $in{$name} = $value; 
    }
}

my $action = $in{'action'};
my $size = $in{'size'};
if($action eq "insert") {
    print "Gear DNS: ".$ENV{'OPENSHIFT_GEAR_DNS'}."\n";
    print "SQL statements:\n";
    print "INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');\n";
    my $sth = $dbh->prepare("SET autocommit=0;") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    if($size eq '') {
        $size = 500000;
    }
    else {
        $size = int($size);
    }
    for($i = 0; $i < $size; $i++) {
        my $sth = $dbh->prepare("INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');") or die $dbh->errstr;
        $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    }
    my $sth = $dbh->prepare("COMMIT;") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    my $sth = $dbh->prepare("SET autocommit=1;") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    print "$size records have been inserted into mysql";
}
elsif($action eq "delete") {
    my $sth = $dbh->prepare("DELETE FROM info;") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    print "Gear DNS: ".$ENV{'OPENSHIFT_GEAR_DNS'}."\n";
    print "All the records have been deleted from mysql database";
}
elsif($action eq "show") {
    my $sth = $dbh->prepare("SELECT COUNT(*) FROM info;") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    my $count = $sth->fetchrow_array();
    print "Gear DNS: ".$ENV{'OPENSHIFT_GEAR_DNS'}."\n";
    if($count == 0) {
        print "There is no record in database\n";
    }
    else {
        print "There are $count records in database\n";
        my $sth = $dbh->prepare("SELECT * FROM info LIMIT 0, 1;") or die $dbh->errstr;
        $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
        $result = $sth->fetchrow_array();
        print "Here is one row: $result\n";
    }
}
else {
    print "[rhc-cartridge]snapshot/restore big mysql data to existing app\n[rhc-cartridge]snapshot/restore big mysql data to new app";
}

my $sth = $dbh->prepare("COMMIT;") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
$sth->finish();
$dbh->disconnect;
