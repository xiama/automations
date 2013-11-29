<%@ page contentType="text/plain" language="java" import="java.sql.*" %>
<%@ page import="javax.naming.*" %>
<%@ page import="java.io.*"  %>
<%@ page import="java.util.*"  %>
<%@ page import="java.text.*"  %>
<%@ page import="javax.naming.*" %>
<%@ page import="javax.sql.*" %>
<%@ page import="com.mysql.jdbc.Driver" %>
<%
out.println("Welcome~");

String action=request.getParameter("action");
out.println("-"+request.getParameter("action")+"-");

if (action == null) {
  action="";
}

Map map = System.getenv();
String url = "jdbc:mysql://" + map.get("OPENSHIFT_MYSQL_DB_HOST") + ":" + map.get("OPENSHIFT_MYSQL_DB_PORT") + "/" + map.get("OPENSHIFT_APP_NAME") + "?user=" + map.get("OPENSHIFT_MYSQL_DB_USERNAME") + "&password=" + map.get("OPENSHIFT_MYSQL_DB_PASSWORD");
Class.forName("com.mysql.jdbc.Driver").newInstance();
Connection connection=DriverManager.getConnection(url);

String context = "";
if (action.equals("create")) {
  Statement statement = connection.createStatement();
  statement.executeUpdate("DROP TABLE IF EXISTS ucctalk");
  statement.executeUpdate("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))");
  statement.executeUpdate("INSERT INTO ucctalk (speaker,title) VALUES ('speaker1', 'title1')");
  ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
  ResultSetMetaData rmeta = rs.getMetaData();
  int numColumns=rmeta.getColumnCount();
  while(rs.next()) {
    context = context + rs.getString(1) + ", " + rs.getString(2) + "\n";
  }
  rs.close();
  statement.close();

  out.print(context);
} else if (action.equals("modify")) {
  Statement statement = connection.createStatement();
  statement.executeUpdate("DROP TABLE IF EXISTS ucctalk");
  statement.executeUpdate("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))");
  statement.executeUpdate("INSERT INTO ucctalk (speaker,title) VALUES ('speaker2', 'title2')");
  ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
  ResultSetMetaData rmeta = rs.getMetaData();
  int numColumns=rmeta.getColumnCount();
  while(rs.next()) {
    context = context + rs.getString(1) + ", " + rs.getString(2) + "\n";
  }
  rs.close();
  statement.close();
  out.print(context);
} else {
  Statement statement = connection.createStatement();
  ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
  ResultSetMetaData rmeta = rs.getMetaData();
  int numColumns=rmeta.getColumnCount();
  while(rs.next()) {
    context = context + rs.getString(1) + ", " + rs.getString(2) + "\n";
  }
  rs.close();
  statement.close();
  out.print(context);
}
connection.close();
%>
