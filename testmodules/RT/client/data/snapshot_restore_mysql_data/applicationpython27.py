#!/usr/bin/python
import os
import commands
import MySQLdb

virtenv = os.environ['OPENSHIFT_HOMEDIR'] + 'python-2.7/virtenv/'
os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python2.7/site-packages')
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

def create_data(speaker_val, title_val):
    content="Welcome~\n"
    try:
        con=MySQLdb.connect(host=os.environ['OPENSHIFT_MYSQL_DB_HOST'], user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'], passwd=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'], db=os.environ['OPENSHIFT_APP_NAME'], port=int(os.environ['OPENSHIFT_MYSQL_DB_PORT']))
        cursor = con.cursor()
        cursor.execute("DROP TABLE IF EXISTS ucctalk")
        cursor.execute("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))")
        cursor.execute("INSERT INTO ucctalk (speaker,title) VALUES ('%s', '%s')" %(speaker_val, title_val))
        cursor.execute("SELECT * FROM ucctalk")
        alldata = cursor.fetchall()
        if alldata:
            for rec in alldata:
                content+=rec[0]+", "+rec[1]+"\n"
        cursor.close()
        con.commit ()
        con.close()
    except Exception, e:
        content = str(e)
    return content

def show_data():
    content="Welcome~\n"
    try:
        con=MySQLdb.connect(host=os.environ['OPENSHIFT_MYSQL_DB_HOST'], user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'], passwd=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'], db=os.environ['OPENSHIFT_APP_NAME'], port=int(os.environ['OPENSHIFT_MYSQL_DB_PORT']))
        cursor = con.cursor()
        cursor.execute("SELECT * FROM ucctalk")
        alldata = cursor.fetchall()
        if alldata:
            for rec in alldata:
                content+=rec[0]+", "+rec[1]+"\n"
        cursor.close()
        con.commit ()
        con.close()
    except Exception, e:
        content = str(e)
    return content


def application(environ, start_response):
	ctype = 'text/plain'

        target_file = "%swsgi_data_test" %(os.environ['OPENSHIFT_DATA_DIR'])

	if environ['PATH_INFO'] == '/health':
		response_body = "1"
	elif environ['PATH_INFO'] == '/env':
		response_body = ['%s: %s' % (key, value)
                    for key, value in sorted(environ.items())]
		response_body = '\n'.join(response_body)
        elif environ['PATH_INFO'] == '/create':
                response_body = create_data("speaker1","title1")
        elif environ['PATH_INFO'] == '/modify':
                response_body = create_data("speaker2","title2")
        elif environ['PATH_INFO'] == '/show':
                response_body = show_data()
	else:
		response_body = 'Welcome to OpenShift'

	status = '200 OK'
	response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
	#
	start_response(status, response_headers)
	return [response_body]

#
# Below for testing only
#
if __name__ == '__main__':
	from wsgiref.simple_server import make_server
	httpd = make_server('localhost', 8051, application)
	# Wait for a single request, serve it and quit.
	httpd.handle_request()
