#!/usr/bin/env perl
use URI::Escape;
print "Content-type: text/plain\r\n\r\n";

# Get parameters in query string
my $param = {};
if(length($ENV{'QUERY_STRING'}) > 0) {
    $buffer = $ENV{'QUERY_STRING'};
    @pairs = split(/&/, $buffer);
    foreach $pair (@pairs){
        ($name, $value) = split(/=/, $pair);
        $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
        $param{$name} = uri_unescape($value);
    }
}

if(not exists($param{'group'})) {
    print "Usage: $ENV{'OPENSHIFT_APP_DNS'}/universal.pl?group=<group>\nValid groups are 'shell', 'mongodb', 'mysql', 'postgresql'\n";
    exit 255
}
if($param{'group'} eq "shell") {
    if(not exists($param{'cmd'})) {
        print "Usage: $ENV{'OPENSHIFT_APP_DNS'}/universal.pl?group=shell&cmd=<shell command>\n";
        exit 1
    }
    my $cmd = $param{'cmd'};
    print "Command: $cmd\n";
    my $output = `$cmd`;
    print "Exit value: $?\n";
    print "===================================Output=====================================\n";
    print $output;
    print "==============================================================================\n";
}
elsif($param{'group'} eq "mysql") {
    print "Mysql operations(not implemented yet)\n";
}
elsif($param{'group'} eq "postgresql") {
    print "Postgresql operations(not implemented yet)\n";
}
elsif($param{'group'} eq "mongodb") {
    print "Mongodb operations(not implemented yet)";
}
elsif($param{'group'} eq "env") {
    foreach $key(keys %ENV){
        print "$key=$ENV{$key}\n";
    }
}
