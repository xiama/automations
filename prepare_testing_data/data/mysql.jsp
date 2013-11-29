<%@ page contentType="text/html" language="java" import="java.sql.*" %>
<%@ page import="javax.naming.*" %>
<%@ page import="java.io.*"  %>
<%@ page import="java.util.*"  %>
<%@ page import="java.text.*"  %>
<%@ page import="javax.naming.*" %>
<%@ page import="javax.sql.*" %>
<%@ page import="com.mysql.jdbc.Driver" %> 


<%
Map map = System.getenv();
String action = request.getParameter("action");
String s = request.getParameter("size");
int size = 0;
if(action == null) {
  action = "";
}
if(s == null) {
    size = 500;
}
else {
    size = Integer.parseInt(s);
}
String url = "jdbc:mysql://#host:#port/#dbname?user=#user&password=#passwd";
Class.forName("com.mysql.jdbc.Driver").newInstance(); 
Connection connection=DriverManager.getConnection(url); 
Statement statement = connection.createStatement();
statement.executeUpdate("CREATE TABLE IF NOT EXISTS info(id INT NOT NULL AUTO_INCREMENT, data CHAR(200), PRIMARY KEY (id));");
statement.executeUpdate("COMMIT;");
if(action.equals("insert")) {
    out.print("Gear DNS: " + map.get("OPENSHIFT_GEAR_DNS") + "<br />");
    out.print("SQL statements:<br />");
    out.print("INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');<br />");
    statement.executeUpdate("SET autocommit=0;");
    for(int i=0; i < size; i++) {
        statement.executeUpdate("INSERT INTO info VALUES(NULL, 'This is testing data for testing snapshoting and restoring big data in mysql database.This is testing data for testing snapshoting and restoring big data in mysql database.');");
    }
    statement.executeUpdate("COMMIT;");
    statement.executeUpdate("SET autocommit=1;");
    out.print(size + " records have been inserted into mysql<br />");
}
else if(action.equals("delete")) {
    out.print("Gear DNS: " + map.get("OPENSHIFT_GEAR_DNS") + "<br />");
    out.print("SQL statements:<br />");
    out.print("DELETE FROM info;<br />");
    statement.executeUpdate("DELETE FROM info;");
    out.print("All the records have been deleted from mysql database");
}
else if(action.equals("show")) {
    out.print("Gear DNS: " + map.get("OPENSHIFT_GEAR_DNS") + "<br />");
    ResultSet rs1 = statement.executeQuery("SELECT COUNT(*) FROM info;");
    if(rs1.next()) {
        if(Integer.parseInt(rs1.getString(1)) == 0) {
            out.print("There is no record in database<br />");
        }
        else {
            out.print("There are " + rs1.getString(1) + " records in database<br />");
        }
    }
    else {
        out.print("There is no record in database<br />");
    }
    rs1.close();
    ResultSet rs2 = statement.executeQuery("SELECT * FROM info LIMIT 0, 1;");
    if(rs2.next()) {
        out.print("Here is one row:<br />" + rs2.getString(1) + ", " + rs2.getString(2));
    }
    rs2.close();
}
else {
    out.println("[rhc-cartridge]snapshot/restore big mysql data to existing app");
    out.println("[rhc-cartridge]snapshot/restore big mysql data to new app");
}
statement.close();
connection.close();
%>
