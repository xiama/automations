<?php

function run_system_cmd($command) {
$io = array();
$p = proc_open($command,
               array(1 => array('pipe', 'w'),
                     2 => array('pipe', 'w')),
               $io);

/* Read output sent to stdout. */
while (!feof($io[1])) {
       $_SESSION['output'] .= htmlspecialchars(fgets($io[1]),
                                               ENT_COMPAT, 'UTF-8');
}

/* Read output sent to stderr. */
while (!feof($io[2])) {
       $_SESSION['output'] .= htmlspecialchars(fgets($io[2]),
                                               ENT_COMPAT, 'UTF-8');
}


fclose($io[1]);
fclose($io[2]);
proc_close($p);

return $_SESSION['output'];
}

function socket_binding($port) {
    error_reporting(E_ALL);
    $address = 'localhost';
    $service_port = $port;
       
    echo "Connecting ".$address.":".$service_port."\n";
    echo "Create socket..........\n";
    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
    if ($socket === false) {
        $error_id = socket_last_error();
        echo "Error: ".$error_id." - ".socket_strerror($error_id)."\n";
        echo "SOCKET CREATE: Fail-1. \n";
    } else {
        echo "SOCKET CREATE: OK-1.\n";
    }
    
    
    echo "Connect socket..........\n";
    $result = socket_connect($socket, $address, $service_port);
    if ($result === false) {
        $error_id = socket_last_error();
        echo "Error: ".$error_id." - ".socket_strerror($error_id)."\n";
        echo "SOCKET CONNECT: Fail-2. \n";
        $RESULT="PASS";
    } else {
        echo "SOCKET CONNECT: OK-2.\n";
        $RESULT="FAIL";
    }
    
    echo "Send Command..........\n";
    $in = "quit\n";
    $result = socket_write($socket, $in, strlen($in));
    if ($result === false) {
        $error_id = socket_last_error();
        echo "Error: ".$error_id." - ".socket_strerror($error_id)."\n";
        echo "SOCKET WRITE: Fail-3. \n";
    } else {
        echo "SOCKET WRITE: OK-3.\n";
    }
    
    echo "Close socket........\n";
    $result = socket_close($socket);
    if ($result === false) {
        $error_id = socket_last_error();
        echo "Error: ".$error_id." - ".socket_strerror($error_id)."\n";
        echo "SOCKET CLOSE: Fail-4. \n";
    } else {
        echo "SOCKET CLOSE: OK-4.\n";
    }

    echo "\n\n\n";

    return $RESULT;
}

echo "Welcome~~~~~~~\n<pre>";
$command = "/bin/sh read_write_libra_important_data_devenv.sh";
$output = run_system_cmd($command);
echo $output;
echo "</pre>";

?>
