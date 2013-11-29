#!/usr/bin/perl
use warnings;
use DBI;
print "Content-type: text/plain\r\n\r\n";
print "Welcome~\n";

$in{"action"} = "";

if (length ($ENV{'QUERY_STRING'}) > 0){
      $buffer = $ENV{'QUERY_STRING'};
      @pairs = split(/&/, $buffer);
      foreach $pair (@pairs){
           ($name, $value) = split(/=/, $pair);
           #print "----".$name."------"."<br>";
           #print "----".$value."------"."<br>";
           $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
           $in{$name} = $value;
      }
}

if ($in{"action"} eq "create") {
    create_data("speaker1", "title1");
}
elsif ($in{"action"} eq "modify") {
    create_data("speaker2", "title2");
}
else {
    default_show();
}

sub default_show {
    my $dbname = "changeme_db";
    my $location = "changeme_url";
    my $port = "changeme_port";
    my $database = "DBI:mysql:$dbname:$location:$port";
    my $db_user = "changeme_username";
    my $db_pass = "changeme_password";
    my $dbh = DBI->connect($database,$db_user,$db_pass) or die "Cannot connect database";

    my $sth = $dbh->prepare("SELECT * FROM ucctalk") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    while (@ary = $sth->fetchrow_array()) {
        print join(", ",@ary),"\n";
    }
    $sth->finish();
    $dbh->disconnect;
}

sub create_data {
    my $dbname = "changeme_db";
    my $location = "changeme_url";
    my $port = "changeme_port";
    my $database = "DBI:mysql:$dbname:$location:$port";
    my $db_user = "changeme_username";
    my $db_pass = "changeme_password";
    my $dbh = DBI->connect($database,$db_user,$db_pass) or die "Cannot connect database";

    my $sth = $dbh->prepare("DROP TABLE IF EXISTS ucctalk") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    my $sth = $dbh->prepare("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    my $sth = $dbh->prepare("INSERT INTO ucctalk (speaker,title) VALUES ('".$_[0]."', '".$_[1]."')") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    my $sth = $dbh->prepare("SELECT * FROM ucctalk") or die $dbh->errstr;
    $sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
    while (@ary = $sth->fetchrow_array()) {
        print join(", ",@ary),"\n";
    }
    $sth->finish();
    $dbh->disconnect;
}

