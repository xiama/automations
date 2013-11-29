#!/usr/bin/perl
print "Content-type: text/plain\r\n\r\n";
$|=1;
foreach $fieldname(keys %ENV){
    print "$ENV[$fieldname]\n";
}
exit;
