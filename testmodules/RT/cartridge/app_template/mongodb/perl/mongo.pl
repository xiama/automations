#!/usr/bin/perl
print "Content-type: text/plain\r\n\r\n";
use MongoDB;

#my $host = "#host";
#my $port = "#port";
#my $dbname = "#dbname";
#my $user = "#user";
#my $passwd = "#passwd";

my $host = $ENV{'OPENSHIFT_MONGODB_DB_HOST'};
my $port = $ENV{'OPENSHIFT_MONGODB_DB_PORT'};
my $dbname = $ENV{'OPENSHIFT_APP_NAME'};
my $user = $ENV{'OPENSHIFT_MONGODB_DB_USERNAME'};
my $passwd = $ENV{'OPENSHIFT_MONGODB_DB_PASSWORD'}; 

my $conn = MongoDB::Connection->new("host" => "mongodb://$host:$port");
$conn->authenticate($dbname, $user, $passwd);
my $db = $conn->$dbname;
my $coll = $db->info;

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

print "Gear DNS: ".$ENV{'OPENSHIFT_GEAR_DNS'}."\n";
if($action eq "insert") {
    if($size eq '') {
        $size = 500000;
    }
    else {
        $size = int($size);
    }
    for($i = 0; $i < $size; $i++) {
        $coll->insert({"data" => "This is testing data for testing snapshoting and restoring big data in mongodb database.This is testing data for testing snapshoting and restoring big data in mongodb database."});
    }
    print "$size records have been inserted into mongodb\n";
}
elsif($action eq "delete") {
    $coll->remove();
    print "All the records have been deleted from mongodb database\n";
}
elsif($action eq "show") {
    my $cursor = $coll->find();
    my $count = $cursor->count();
    if($count == 0) {
        print "There is no record in database\n";
    }
    else {
        my $doc = $cursor->next();
        print "There are $count records in database\nHere's one record: $doc->{'data'}";
    }
}
else {
    print "[US2103][RT]Alter domain for a scaling perl app which having mongodb added";
}
