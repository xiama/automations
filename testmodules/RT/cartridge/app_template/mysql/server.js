#!/bin/env node
//  OpenShift sample Node application

var express = require('express');
var fs      = require('fs');
var mysql   = require('mysql');
//var client = mysql.createClient({
//    user:'#mysql_user#',
//    password :'#mysql_passwd#'
//});
//client.host ='#mysql_host#';
//client.port = #mysql_port#;
//client.database = '#mysql_dbname#';

var client = mysql.createClient({
    user: process.env.OPENSHIFT_MYSQL_DB_USERNAME,
    password : process.env.OPENSHIFT_MYSQL_DB_PASSWORD
});
client.host = process.env.OPENSHIFT_MYSQL_DB_HOST;
client.port = process.env.OPENSHIFT_MYSQL_DB_PORT;
client.database = process.env.OPENSHIFT_APP_NAME;


//  Local cache for static content [fixed and loaded at startup]
var zcache = { 'index.html': '' };
zcache['index.html'] = fs.readFileSync('./index.html'); //  Cache index.html

// Create "express" server.
var app  = express.createServer();


/*  =====================================================================  */
/*  Setup route handlers.  */
/*  =====================================================================  */

// Handler for GET /health
app.get('/health', function(req, res){
    res.send('1');
});

// Handler for GET /asciimo
app.get('/asciimo', function(req, res){
    var link="https://a248.e.akamai.net/assets.github.com/img/d84f00f173afcf3bc81b4fad855e39838b23d8ff/687474703a2f2f696d6775722e636f6d2f6b6d626a422e706e67";
    res.send("<html><body><img src='" + link + "'></body></html>");
});

// Handler for GET /
app.get('/', function(req, res){
    res.send(zcache['index.html'], {'Content-Type': 'text/html'});
});
// Handler for GET /data1.js
app.get('/data1.js', function(req, res){
    client.query("DROP TABLE IF EXISTS info");
    client.query("CREATE TABLE info(id INT PRIMARY KEY, data VARCHAR(20))");
    client.query("INSERT INTO info VALUES(1, '#str_random1#')");
    //client.end();
    res.send('Please visit /show.js to see the data', {'Content-Type': 'text/plain'});
});
// Handler for GET /data2.js
app.get('/data2.js', function(req, res){
    client.query("DROP TABLE IF EXISTS info");
    client.query("CREATE TABLE info(id INT PRIMARY KEY, data VARCHAR(20))");
    client.query("INSERT INTO info VALUES(1, '#str_random2#')");
    //client.end();
    res.send('Please visit /show.js to see the data', {'Content-Type': 'text/plain'});
});
// Handler for GET /show.js
app.get('/show.js', function(req, res){
    var gear_dns = process.env.OPENSHIFT_GEAR_DNS;
    client.query(
        'SELECT data FROM info',
        function selectCb(err, results, fields) {
            if (err) {
                res.send('Failed to get data from database', {'Content-Type': 'text/plain'});
                throw err;
            }
            else {
                res.send("GEAR DNS: " + gear_dns + "<br />Data: " + results[0]['data'], {'Content-Type': 'text/plain'});
            }
        }
    );
    //client.end();
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

