#!/bin/env node
var express = require('express');
var mysql   = require('mysql');
var client = mysql.createClient({
    user: process.env.OPENSHIFT_MYSQL_DB_USERNAME,
    password : process.env.OPENSHIFT_MYSQL_DB_PASSWORD
});
client.host = process.env.OPENSHIFT_MYSQL_DB_HOST;
client.port = process.env.OPENSHIFT_MYSQL_DB_PORT;
client.database = process.env.OPENSHIFT_APP_NAME;



//  Local cache for static content [fixed and loaded at startup]

// Create "express" server.
var app  = express.createServer();

client.query("CREATE TABLE IF NOT EXISTS info(id INT NOT NULL AUTO_INCREMENT, data CHAR(200), PRIMARY KEY (id));");
client.query("COMMIT;")
/*  =====================================================================  */
/*  Setup route handlers.  */
/*  =====================================================================  */

// Handler for GET /health
app.get('/health', function(req, res){
    res.send('1');
});
// Handler for GET /
app.get('/', function(req, res){
    res.send('[rhc-cartridge]snapshot/restore big mysql data to existing app\n[rhc-cartridge]snapshot/restore big mysql data to new app\n', {'Content-Type': 'text/plain'});
});
// Handler for GET /insert
app.get('/insert', function(req, res){
    size = (+req.query["size"]);
    response_body = "Gear DNS: " + process.env.OPENSHIFT_GEAR_DNS + "\n";
    response_body += "SQL statements:\n";
    response_body += "INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');\n\n";
    client.query("SET autocommit=0;");
    for(var i=0; i < size; i++) {
        client.query("INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');");
    }
    client.query("COMMIT;");
    client.query("SET autocommit=1;");
    response_body += size + " records have been inserted into mysql\n";
    res.send(response_body, {'Content-Type': 'text/plain'});
});
// Handler for GET /delete
app.get('/delete', function(req, res){
    response_body = "Gear DNS: " + process.env.OPENSHIFT_GEAR_DNS + "\n";
    response_body += "SQL statement: DELETE FROM info;\n";
    response_body += "All the records have been deleted from mysql database";
    client.query("DELETE FROM info;");
    res.send(response_body, {'Content-Type': 'text/plain'});
});
// Handler for GET /show
app.get('/show', function(req, res){
    client.query(
        'SELECT COUNT(*) AS count, data FROM info;',
        function selectCb(err, results, fields) {
            var response_body = "Gear DNS: " + process.env.OPENSHIFT_GEAR_DNS + "\n";
            response_body += "SQL statement: SELECT * from info;\n";
            if (err) {
                res.send('Failed to count records in database', {'Content-Type': 'text/plain'});
                throw err;
            }
            else {
                if(results[0]['count'] == 0) {
                    response_body += "There is no record in database\n";
                }
                else {
                    response_body += "There are " + results[0]['count'] + " records in database\n";
                    response_body += "Here is one row: " + results[0]['data'] + "\n";
                }
            }
            res.send(response_body, {'Content-Type': 'text/plain'});
        }
    );
});


//  Get the environment variables we need.
var ipaddr  = process.env.OPENSHIFT_INTERNAL_IP;
var port    = process.env.OPENSHIFT_INTERNAL_PORT || 8080;

if (typeof ipaddr === "undefined") {
   console.warn('No OPENSHIFT_INTERNAL_IP environment variable');
}

//  terminator === the termination handler.
function terminator(sig) {
   if (typeof sig === "string") {
      console.log('%s: Received %s - terminating Node server ...',
                  Date(Date.now()), sig);
      process.exit(1);
   }
   console.log('%s: Node server stopped.', Date(Date.now()) );
}

//  Process on exit and signals.
process.on('exit', function() { terminator(); });

['SIGHUP', 'SIGINT', 'SIGQUIT', 'SIGILL', 'SIGTRAP', 'SIGABRT', 'SIGBUS',
 'SIGFPE', 'SIGUSR1', 'SIGSEGV', 'SIGUSR2', 'SIGPIPE', 'SIGTERM'
].forEach(function(element, index, array) {
    process.on(element, function() { terminator(element); });
});

//  And start the app on that interface (and port).
app.listen(port, ipaddr, function() {
   console.log('%s: Node server started on %s:%d ...', Date(Date.now() ),
               ipaddr, port);
});

