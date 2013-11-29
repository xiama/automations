<%@ page contentType="text/plain" language="java" import="java.sql.*,javax.naming.*,java.io.*,java.util.*,java.net.*,java.util.regex.*,java.text.*" %>
<%!
public String parseEnvvar(String s)
{
    String result = new String(s);
    Pattern p = Pattern.compile("\\$[A-Z_]+");
    Matcher m = p.matcher(s);
    System.out.println("Start matching");
    while(m.find()) {
        String tmp = m.group();
        System.out.println(tmp);
    }
    System.out.println("Stop matching");
    return "linux";
}
%>
<%
Map map = System.getenv();
String group = request.getParameter("group");
if(group == null) {
    out.println("Usage: " + map.get("OPENSHIFT_APP_DNS") + "/universal.jsp?group=<group>\nValid groups are 'shell', 'mongodb', 'mysql', 'postgresql'");
    return;
}
group = URLDecoder.decode(group);
if(group.equals("shell")) {
    String cmd = request.getParameter("cmd");
    if(cmd == null) {
        out.println("Usage: " + map.get("OPENSHIFT_APP_DNS") + "/universal.jsp?group=shell&cmd=<shell command>");
        return;
    }
    cmd = URLDecoder.decode(cmd);
    out.println("Command: " + cmd);
    //Process p = Runtime.getRuntime().exec(cmd);
    Process p = Runtime.getRuntime().exec("echo $OPENSHIFT_REPO_DIR");
    out.println(parseEnvvar("echo $OPENSHIFT_REPO_DIR"));
    p.waitFor();
    out.println("Exit value: " + p.exitValue());
    out.println("===================================Output=====================================");
    BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
    String line = null;
    while((line = input.readLine()) != null) {
        out.println(line);
    }
    out.println("==============================================================================");
}
else if(group.equals("env")) {
    Set<String> keys = map.keySet();
    Iterator<String> i = keys.iterator();
    while(i.hasNext()) {
        String key = i.next();
        out.println(key + "=" + map.get(key));
    }
}
else if(group.equals("mysql")) {
    String fullsql = request.getParameter("sql");
    if(fullsql == null) {
        out.println("Usage: " + map.get("OPENSHIFT_APP_DNS") + "/universal.jsp?group=mysql&sql=<SQL statement>");
        return;
    }
    fullsql = URLDecoder.decode(fullsql);
    out.println("Full SQL statements: " + fullsql);
    String[] sqls = fullsql.split(";");
    String url = "jdbc:mysql://" + map.get("OPENSHIFT_MYSQL_DB_HOST") + ":" + map.get("OPENSHIFT_MYSQL_DB_PORT") + "/" + map.get("OPENSHIFT_APP_NAME") + "?user=" + map.get("OPENSHIFT_MYSQL_DB_USERNAME") + "&password=" + map.get("OPENSHIFT_MYSQL_DB_PASSWORD");
    out.println("MySQL Connection URL: " + url + "\n");
    Class.forName("com.mysql.jdbc.Driver").newInstance();
    Connection connection=DriverManager.getConnection(url);
    for(int j=0; j < sqls.length; j++) {
        String sql = sqls[j].trim();
        out.println("SQL statement: " + sql);
        Statement statement = connection.createStatement();
        if(sql.equals("")) {
            continue;
        }
        else if(sql.toLowerCase().contains("select")) {
            ResultSet rs = statement.executeQuery(sql);
            ResultSetMetaData rsmd = rs.getMetaData();
            int NumOfCol = rsmd.getColumnCount();
            for(int i=1; i <= NumOfCol; i++) {
                out.print(rsmd.getColumnLabel(i) + "\t\t");
            }
            out.print("\n");
            while(rs.next()) {
                for(int i=1; i <= NumOfCol; i++) {
                    out.print(rs.getString(i) + "\t\t");
                }
                out.print("\n");
            }
            rs.close();
        }
        else {
            statement.executeUpdate(sql);
        }
        statement.close();
        out.print("\n");
    }
    connection.close();
}
else {
    out.println("Usage: " + map.get("OPENSHIFT_APP_DNS") + "/universal.jsp?group=<group>\nValid groups are 'shell', 'mongodb', 'mysql', 'postgresql', 'env'");
    return;
}
%>
