<%@ page contentType="text/html" language="java" import="java.sql.*" %>
<%@ page import="javax.naming.*" %>
<%@ page import="java.io.*"  %>
<%@ page import="java.util.*"  %>

<%
Map map = System.getenv();
String action = request.getParameter("action");
String size = request.getParameter("size");
if(action == null) {
  action = "";
}
if(size == null) {
    size = "300";
}
if(action.equals("create")) {
    String cmd = "dd if=/dev/urandom of=" + map.get("OPENSHIFT_DATA_DIR") + "bigfile bs=1M count=" + size;
    out.println("Command: " + cmd);
    Process p = Runtime.getRuntime().exec(cmd);
    BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
    String line = null;
    while((line = input.readLine()) != null) {
        out.println(line);
    }
    out.println("<br />");
    p.waitFor();
    if(p.exitValue() == 0) {
        out.println("The bigfile has been created.");
    }
    else {
        out.println("Failed to create bigfile under OPENSHIFT_DATA_DIR");
    }
}
else if(action.equals("delete")) {
    String cmd = "rm " + map.get("OPENSHIFT_DATA_DIR") + "bigfile";
    out.println("Command: " + cmd);
    Process p = Runtime.getRuntime().exec(cmd);
    BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
    String line = null;
    while((line = input.readLine()) != null) {
        out.println(line);
    }
    out.println("<br />");
    p.waitFor();
    if(p.exitValue() == 0) {
        out.println("The bigfile has been deleted.");
    }
    else {
        out.println("Failed to delete bigfile under OPENSHIFT_DATA_DIR");
    }
}
else if(action.equals("show")) {
    String cmd = "ls -lh " + map.get("OPENSHIFT_DATA_DIR") + "bigfile";
    out.println("Command: " + cmd);
    Process p = Runtime.getRuntime().exec(cmd);
    BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
    String line = null;
    while((line = input.readLine()) != null) {
        out.println(line);
    }
    out.println("<br />");
    p.waitFor();
    if(p.exitValue() == 0) {
        out.println("The bigfile exists.");
    }
    else {
        out.println("The bigfile doesnot exist.");
    }
}
%>
