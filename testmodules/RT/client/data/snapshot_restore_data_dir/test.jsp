<%@ page import="java.io.*"  %>
<%@ page import="java.util.*"  %>

<%!
   public void write_file(String file, String context)
   {
    try {
        PrintWriter pw = new PrintWriter(new FileOutputStream(file));
        pw.println(context);
        pw.close();
      } catch (FileNotFoundException e ){
        }
   }

   public List exec_shell_cmd(String cmd_str)
   {
    List list = new ArrayList();
    try {
       String[] cmd = {"/bin/sh", "-c", cmd_str};
       String output = "";
       String line;
       int ret = 0;
       Process p = Runtime.getRuntime().exec(cmd);
       BufferedReader bri = new BufferedReader(new InputStreamReader(p.getInputStream()));
       BufferedReader bre = new BufferedReader(new InputStreamReader(p.getErrorStream()));
       while ((line = bri.readLine()) != null) {
           output = output + line;
       }
       bri.close();
       while ((line = bre.readLine()) != null) {
           output = output + line;
       }
       bre.close();
       p.waitFor();
       ret = p.exitValue();
       list.add(ret);
       list.add(output);
     } catch (Exception err) {
       }
    return list;
   }

%>

<%
out.println("Welcome~");

String action=request.getParameter("action");
out.println("-"+request.getParameter("action")+"-");

if (action == null) {
  action="";
}


String target_file = System.getenv().get("OPENSHIFT_DATA_DIR") + "jbossas_data_test";
//out.println(target_file);
String str = "";
String cmd = "";
int ret = 112;
List list;

if (action.equals("create")) {
    out.println("Creating test file: " + target_file);
    str = "snapshot_restore_data_dir_test1";
    cmd = "echo " + str + " >" + target_file;
    out.println("Command: " + cmd);
    list = exec_shell_cmd(cmd);
    out.println(list.get(1));
    ret = (Integer)list.get(0);
    out.println("Return: " + ret);


    cmd = "cat " + target_file;
    out.println("Command: " + cmd);
    list = exec_shell_cmd(cmd);
    out.println(list.get(1));

    if (ret == 0) {
         out.println("RESULT=0");
    } else {
         out.println("RESULT=1");
    }    
} else if (action.equals("modify")) {
    out.println("Modifying test file: " + target_file);
    str = "snapshot_restore_data_dir_test2";
    cmd = "echo " + str + " >" + target_file;
    out.println("Command: " + cmd);
    list = exec_shell_cmd(cmd);
    out.println(list.get(1));
    ret = (Integer)list.get(0);
    out.println("Return: " + ret);


    cmd = "cat " + target_file;
    out.println("Command: " + cmd);
    list = exec_shell_cmd(cmd);
    out.println(list.get(1));

    if (ret == 0) {
         out.println("RESULT=0");
    } else {
         out.println("RESULT=1");
    }

} else {
    cmd = "cat " + target_file;
    out.println("Command: " + cmd);
    list = exec_shell_cmd(cmd);
    out.println(list.get(1));

}
%>


