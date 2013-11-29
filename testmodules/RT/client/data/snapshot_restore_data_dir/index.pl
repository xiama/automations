#!/usr/bin/perl
use warnings;

print "Content-type: text/html\r\n\r\n";
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

$target_file = $ENV{'OPENSHIFT_DATA_DIR'}."perl_data_test";

if ($in{"action"} eq "create") {
    $key_string = "snapshot_restore_data_dir_test1";
    create_file($target_file, $key_string);
} 
elsif ($in{"action"} eq "modify") {
    $key_string = "snapshot_restore_data_dir_test2";
    create_file($target_file, $key_string);
}
else {
    default_show($target_file);
}

sub default_show {
    $command = "cat ".$_[0]." 2>&1";
    print "Command: ".$command."\n";
    $output = `$command`;
    $ret_tmp = $?;
    print $output."\n";
}


sub create_file {
    $command1 = "echo ".$_[1]." >".$_[0]." 2>&1";
    print "Command 1: ".$command1."\n";
    $output = `$command1`;
    $ret1 = $?;
    print $output."\n";

    $command = "cat ".$_[0]." 2>&1";
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

