<%@ page contentType="text/plain" language="java" import="java.sql.*" %>
<%@ page import="javax.naming.*" %>
<%@ page import="java.io.*"  %>
<%@ page import="java.util.*"  %>
<%@ page import="java.text.*"  %>
<%@ page import="javax.naming.*" %>
<%@ page import="javax.sql.*" %>
<%
InitialContext ctx = new InitialContext();
DataSource ds = (DataSource) ctx.lookup("java:comp/env/jdbc/PostgreSQLDS");
Connection connection=ds.getConnection();
Statement statement = connection.createStatement();
ResultSet rs = statement.executeQuery("SELECT data FROM info;");
ResultSetMetaData rmeta = rs.getMetaData();
int numColumns=rmeta.getColumnCount();
while(rs.next()) {
    out.print(rs.getString(1));
}
rs.close();
statement.close();
connection.close();
%>
