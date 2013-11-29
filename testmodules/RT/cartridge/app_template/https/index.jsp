<HTML>
<HEAD>
<TITLE>Getting Header Data</TITLE>
</HEAD>

<BODY>
<H1>Getting Header Data</H1>
<FORM ACTION="basic.jsp" METHOD="POST">
<INPUT TYPE="submit" VALUE="Submit">
</FORM>
</BODY>
</HTML>

#cat basic.jsp

<HTML>
<HEAD>
<TITLE>Reading Header Information</TITLE>
</HEAD>

<BODY>
<H1>Reading Header Information</H1>
        Here are the request headers and their data:
<BR>
<% java.util.Enumeration names = request.getHeaderNames();
        while(names.hasMoreElements()){
            String name = (String) names.nextElement();
            out.println(name + ":<BR>" + request.getHeader(name) + "<BR><BR>");
        }
        %>
</BODY>
</HTML>
