<%@ page session="false" %>
<%@ page contentType="text/html" language="java" %>
<%@ page import="javax.naming.*" %>
<%@ page import="java.io.*"  %>
<%@ page import="java.util.*"  %>
<%@ page import="java.text.*"  %>
<%@ page import="javax.naming.*" %>
<%@ page import="com.mongodb.*" %>

<%
String action = request.getParameter("action");
String s = request.getParameter("size");
int size = 0;
if(action == null) {
  action = "";
}
if(s == null) {
    size = 500000;
}
else {
    size = Integer.parseInt(s);
}

Map map = System.getenv();
out.print("Gear DNS: " + map.get("OPENSHIFT_GEAR_DNS") + "<br />");

String host = System.getenv("OPENSHIFT_MONGODB_DB_HOST");
int port = Integer.parseInt(System.getenv("OPENSHIFT_MONGODB_DB_PORT"));
String dbname = System.getenv("OPENSHIFT_APP_NAME");
String user = System.getenv("OPENSHIFT_MONGODB_DB_USERNAME");
String passwd = System.getenv("OPENSHIFT_MONGODB_DB_PASSWORD");
Mongo m = new Mongo(host, port);
DB db = m.getDB(dbname);
boolean auth = db.authenticate(user, passwd.toCharArray());
if(auth == true) {
    DBCollection coll = db.getCollection("info");
    if(action.equals("insert")) {
        for(int i=0; i < size; i++) {
            BasicDBObject doc = new BasicDBObject();
            doc.put("data", "This is testing data for testing snapshoting and restoring big data in mongodb database.This is testing data for testing snapshoting and restoring big data in mongodb database.");
            coll.insert(doc);
            doc = null;
        }
        out.print(size + " records have been inserted into mongodb<br />");
    }
    else if(action.equals("delete")) {
        coll.drop();
        out.print("All the records have been deleted from mongodb database<br />");
    }
    else if(action.equals("show")) {
        long count = coll.getCount();
        if(count > 0) {
            out.print("There are " + Long.toString(count) + " records in database<br />Here's one record:");
            DBObject myDoc = coll.findOne();
            out.print(myDoc.get("data") + "<br />");
        }
        else {
            out.print("There is no record in database<br />");
        }
    }
    else {
    }
}
else {
    out.print("Authentication failed<br />");
}
m.close();
%>
