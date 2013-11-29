#!/bin/env node
//  OpenShift sample Node application

var express = require('express');
var fs      = require('fs');
var pg      = require('pg').native;
//var conString  = "tcp://#pgsql_user#:#pgsql_passwd#@#pgsql_host#:#pgsql_port#/#pgsql_dbname#";
var conString = "tcp://" + process.env.OPENSHIFT_POSTGRESQL_DB_USERNAME + ":" + process.env.OPENSHIFT_POSTGRESQL_DB_PASSWORD + "@" + process.env.OPENSHIFT_POSTGRESQL_DB_HOST + ":" + process.env.OPENSHIFT_POSTGRESQL_DB_PORT + "/" + process.env.OPENSHIFT_APP_NAME;

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
// Handler for GET /data1
app.get('/data1.js', function(req, res){
    var client = new pg.Client(conString);
    client.connect();
    client.query("DROP TABLE IF EXISTS info");
    client.query("CREATE TABLE info(id integer PRIMARY KEY, data text)");
    client.query("INSERT INTO info VALUES(1, '#str_random1#')");
    client.end();
    res.send('Please visit /show.js to see the data', {'Content-Type': 'text/plain'});
});
// Handler for GET /data2
app.get('/data2.js', function(req, res){
    var client = new pg.Client(conString);
    client.connect();
    client.query("DROP TABLE IF EXISTS info");
    client.query("CREATE TABLE info(id integer PRIMARY KEY, data text)");
    client.query("INSERT INTO info VALUES(1, '#str_random2#')");
    client.end();
    res.send('Please visit /show.js to see the data', {'Content-Type': 'text/plain'});
});
// Handler for GET /show
app.get('/show.js', function(req, res){
    var client = new pg.Client(conString);
    client.connect();
    var query = client.query("SELECT data FROM info");
    query.on('row', function(row) {
        result = row.data;
    });
    query.on('error', function(error) {
        client.end();
        res.send('Failed to get data from database', {'Content-Type': 'text/plain'});
    });
    query.on('end', function() {
        client.end();
        res.send(result, {'Content-Type': 'text/plain'});
    });
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

