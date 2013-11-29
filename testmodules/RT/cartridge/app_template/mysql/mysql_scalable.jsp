<%@ page contentType="text/plain" %>
<%@ page trimDirectiveWhitespaces="true" %>
<%@ page import="java.sql.*" %>
<%@ page import="java.lang.*"%>
<%
/*
 * !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 * ! Do not forget to add mysql-connector-java to your pom.xml as a dependency !
 * !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 */

try {
    Class.forName("com.mysql.jdbc.Driver");
} catch (ClassNotFoundException e) {
    out.println("Driver not loaded: "+e.getMessage());
    e.printStackTrace();
}

String MYSQL_HOST = System.getenv("OPENSHIFT_MYSQL_DB_HOST");
String MYSQL_PORT = System.getenv("OPENSHIFT_MYSQL_DB_PORT");
String MYSQL_DB = System.getenv("OPENSHIFT_APP_NAME");
String MYSQL_USER = System.getenv("OPENSHIFT_MYSQL_DB_USERNAME");
String MYSQL_PASSWORD = System.getenv("OPENSHIFT_MYSQL_DB_PASSWORD");

//String connectionURL = "jdbc:mysql://##mysql_url##:##mysql_port##/##mysql_database##?user=##mysql_user##&password=##mysql_password##&autoReconnect=true&failOverReadOnly=false&maxReconnects=10"; 
String connectionURL = "jdbc:mysql://" + MYSQL_HOST + ":" + MYSQL_PORT + "/" + MYSQL_DB + "?user=" + MYSQL_USER + "&password=" + MYSQL_PASSWORD + "&autoReconnect=true&failOverReadOnly=false&maxReconnects=10"; 
Connection connection = null;

try {
    connection = DriverManager.getConnection(connectionURL);
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
        out.print("\n");
    }
} catch ( SQLException err ) {
    out.println(err.getMessage());
} finally{
    if ( connection != null ) {
        connection.close();
    }
}


%>
