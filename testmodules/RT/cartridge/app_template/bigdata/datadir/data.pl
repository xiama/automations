#!/usr/bin/perl
print "Content-type: text/plain\r\n\r\n";

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
if($size eq '') {
    $size = "300";
}

if($action eq "create") {
    my $cmd = "dd if=/dev/urandom of=".$ENV{'OPENSHIFT_DATA_DIR'}."bigfile bs=1M count=".$size;
    print "Command: ".$cmd."\n";
    my $ret = system($cmd); 
    if($ret == 0) {
        print "The bigfile has been created.\n";
    }
    else {
        print "Failed to create bigfile under OPENSHIFT_DATA_DIR\n";
    }
}
elsif($action eq "delete") {
    my $cmd = "rm -f ".$ENV{'OPENSHIFT_DATA_DIR'}."bigfile";
    print "Command: ".$cmd."\n";
    my $ret = system($cmd);
    if($ret == 0) {
        print "The bigfile has been deleted.\n";
    }
    else {
        print "Failed to delete the bigfile\n";
    }
}
elsif($action eq "show") {
    my $filepath = $ENV{'OPENSHIFT_DATA_DIR'}."bigfile";
    my $cmd = "ls -lh ".$filepath;
    print "Command: ".$cmd."\n";
    if(-e $filepath) {
        my $output = `$cmd`;
        print "Output: ".$output."\n";
        print "The bigfile exists.\n";
    }
    else {
        print "The bigfile doesnot exist.\n";
    }
}
else {
    print "[rhc-cartridge]snapshot/restore big mysql data to existing app\n[rhc-cartridge]snapshot/restore big mysql data to new app\n";
}
