<%@ page contentType="text/plain" %>
<%@ page trimDirectiveWhitespaces="true" %>
<%@ page import="java.io.BufferedReader" %>
<%@ page import="java.io.InputStreamReader" %>
<%@ page import="java.util.regex.Pattern" %>
<%@ page import="java.util.regex.Matcher" %>
<%@ page import="java.util.ArrayList" %>
<%@ page import="java.util.Collections" %>
<%@ page import="java.net.URL" %>
<%@ page import="java.net.URLClassLoader" %>
<%@ page import="java.io.File" %>
<%@ page import="java.lang.reflect.Field" %>

<%

Process findrpm = Runtime.getRuntime().exec("find /opt/ -print");
BufferedReader findrpm_result = new BufferedReader(new InputStreamReader(findrpm.getInputStream()));

// Looking for latest JGroups JAR file
String line;
ArrayList<String> jgroups_jars = new ArrayList();
Pattern p = Pattern.compile("^/opt/jboss-as.+main/jgroups.+\\.jar$");

while ( (line = findrpm_result.readLine()) != null ) {
	Matcher m = p.matcher(line);
	if ( m.find() ) {
		jgroups_jars.add(line);
	}
}

Collections.sort(jgroups_jars, String.CASE_INSENSITIVE_ORDER);
Collections.reverse(jgroups_jars);
String latest_jgroups_jar = jgroups_jars.get(0);

// Adding JGroups JAR file to CLASSPATH
String original_classpath = System.getProperty("java.class.path");
URL[] new_classpath_array = {
	new File(original_classpath).toURL(),
	new File(latest_jgroups_jar).toURL()
};

// Printing version info
URLClassLoader ucl = new URLClassLoader(new_classpath_array);
Class jgroups_version_class = Class.forName("org.jgroups.Version", true, ucl);
Field jgroups_version_field = jgroups_version_class.getField("version");
out.println(jgroups_version_field.get(null));

%>
