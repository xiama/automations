<%@ page contentType="text/html" language="java" import="java.sql.*" %>
<%@ page import="javax.naming.*" %>
<%@ page import="javax.sql.*" %>
<%
InitialContext ctx = new InitialContext();
DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/PostgreSQLDS");
Connection connection=ds.getConnection();
Statement statement = connection.createStatement();
statement.executeUpdate("DROP TABLE IF EXISTS info;");
statement.executeUpdate("CREATE TABLE info(id integer PRIMARY KEY, data text);");
statement.executeUpdate("INSERT INTO info VALUES(1, '#str_random2#');");
statement.close();
out.print("Please visit /show.jsp to see the data");
connection.close();
%>
