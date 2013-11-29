<%@ page contentType="text/html" language="java" import="java.sql.*" %>
<%@ page import="javax.naming.*" %>
<%@ page import="javax.sql.*" %>


<%
out.println("Welcome~");

String action=request.getParameter("action");
out.println("-"+request.getParameter("action")+"-");

if (action == null) {
  action="";
}

String context = "";
if (action.equals("create")) {
  InitialContext ctx = new InitialContext();
  DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MysqlDS");
  Connection connection=ds.getConnection();
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
  connection.close();

  out.print(context);
} else if (action.equals("modify")) {
  InitialContext ctx = new InitialContext();
  DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MysqlDS");
  Connection connection=ds.getConnection();
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
  connection.close();

  out.print(context);
} else {
  InitialContext ctx = new InitialContext();
  DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MysqlDS");
  Connection connection=ds.getConnection();
  Statement statement = connection.createStatement();
  ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
  ResultSetMetaData rmeta = rs.getMetaData();
  int numColumns=rmeta.getColumnCount();
  while(rs.next()) {
    context = context + rs.getString(1) + ", " + rs.getString(2) + "\n";
  }
  rs.close();
  statement.close();
  connection.close();

  out.print(context);
}


%>
