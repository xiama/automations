<%@ page contentType="text/html" language="java" import="java.sql.*" %>
<%@ page import="javax.naming.*" %>
<%@ page import="javax.sql.*" %>
<%
InitialContext ctx = new InitialContext();
DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MysqlDS");
Connection connection=ds.getConnection();
Statement statement = connection.createStatement();
statement.executeUpdate("DROP TABLE IF EXISTS ucctalk");
statement.executeUpdate("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))");
statement.executeUpdate("INSERT INTO ucctalk (speaker,title) VALUES ('Jeremy Zawodny', 'Optimizing MySQL'), ('Sanja Byelkin', 'Sub-Queries in MySQL'), ('Tim Bunce', 'Advanced Perl DBI')");
ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
ResultSetMetaData rmeta = rs.getMetaData();
int numColumns=rmeta.getColumnCount();
while(rs.next()) {
    out.print(rs.getString(1));
    out.print(", ");
    out.print(rs.getString(2));
    out.print("<br>");
}
rs.close();
statement.close();
connection.close();
%>
