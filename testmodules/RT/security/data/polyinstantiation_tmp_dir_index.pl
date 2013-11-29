#!/usr/bin/perl
use warnings;

print "Content-type: text/html\r\n\r\n";

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
    create_tmp_file();
} else {
    default_show();
}

sub default_show {
    $command1 = "ls -l /tmp/perl_tmp_test 2>&1 && ls -l /var/tmp/perl_var_tmp_test 2>&1";
    print "Command 1: ".$command1."\n";
    $output = `$command1`;
    $ret1 = $?;
    print $output."\n"; 

    $command = "ls -l /tmp 2>&1";
    print "Command: ".$command."\n";
    $output = `$command`;
    $ret_tmp = $?;
    print $output."\n";

    if($ret1 == 0){
        print "RESULT=0"."\n";
    } else {
        print "RESULT=1"."\n";
    }
}


sub create_tmp_file {
    $command1 = "touch /tmp/perl_tmp_test 2>&1";
    print "Command 1: ".$command1."\n";
    $output = `$command1`;
    $ret1 = $?;
    print $output."\n";

    $command2 = "touch /var/tmp/perl_var_tmp_test 2>&1";
    print "Command 2: ".$command2."\n";
    $output = `$command2`;
    $ret2 = $?;
    print $output."\n";

    $command = "ls -l /tmp 2>&1";
    print "Command: ".$command."\n";
    $output = `$command`;
    $ret_tmp = $?;
    print $output."\n";

    if(($ret1 == 0) && ($ret2 == 0)){
        print "RESULT=0"."\n";
    } else {
        print "RESULT=1"."\n";
    }
}

