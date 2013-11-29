<?php
#
# Run multifork.py
#
# actions:
#   start - run as a daemon
#   stop  - stop daemon 
#   status - query daemon status
#   clean - remove logs and any leftover processes
#   onetime - run once without forking
#
#  
# parameters:
#   daemon - fork
#   logfile - where to write logs
#   pidfile - where to write the PID for controls
#   format - the output format of the logs
#   duration - how long to run
#   count - the number of processes to try to start

$scriptfile = "python multifork.py";

$defaults = 
  array(
	'debug' => FALSE,
	'verbose' => FALSE,
	'noop' => FALSE,
	'help' => FALSE,
	'daemon' => FALSE,
	'logfile' =>  NULL,
	'pidfile' => NULL,
	'format' => NULL,
	'duration' => NULL,
	'count' => NULL
	);

$formats = array('text', 'html', 'xml', 'json');

$shortopts = "dvnhl:p:f:D:c:";

$longopts = 
  array(
	"debug",
	"verbose",
	"dryrun",
	"help",
	"daemon",
	"logfile:",
	"pidfile:",
	"format:",
	"duration:",
	"count:"
	);

$optmap = array(
		"d" => "debug",
		"v" => "verbose",
		"n" => "dryrun",
		"h" => "help",
		"l" => "logfile",
		"p" => "pidfile",
		"f" => "format",
		"D" => "duration",
		"c" => "count"
		);

if (isset($_SERVER['argc'])) {
  #
  # Only collect options from CLI if called that way
  #
  $opt = getopt($shortopts, $longopts);

  # map the short to long and remove them.
  $shortkeys = array_keys($optmap);
  foreach ($opt as $optkey => $optvalue) {
    if (array_key_exists($optkey, $optmap)) {
      $longkey = $optmap[$optkey];
      if (! array_key_exists($longkey, array_keys($opt))) {
	$opt[$longkey] = $optvalue;
      }
      unset($opt[$optkey]);
    }
  }
} else {
  # Collect options from server GET/POST
  $dummy = 0;
}

exec("$scriptfile --format text --duration 10 --count 300" , $output);
$result = join("\n", $output);
print $result;
?>
