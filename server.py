#!/usr/bin/python

# Client side command to communicate to this server
# curl -d @ssh.py "http://<IP>:<port>/put_ssh_key/"

import string,os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from SocketServer import ThreadingMixIn
paths = dict()
class POST_check:
    def __init__(self, handler):
        self.handler=handler


    def sendResponse(self, status_number):
        self.handler.send_response(status_number)
        self.handler.send_header('server','POST_check')
        self.handler.end_headers()

    def print_post(self, temp):
        print temp
        self.send_response(200)

    def handle_req(self,temp):
        print "Handle Request" + temp
        (tmp, ignore, temp) = temp.partition('/')
        (operation, ignore, temp) = temp.partition('/')

        print "handle_roa_request" + operation
        
        if operation == 'file_data':
            self.file_data()
            
        if operation == 'file':
            self.file()

    def file(self):
        len = int(self.handler.headers.get('Content-Length'))
        file_name=self.handler.rfile.read(len)
        f=open('/home/shardul/' + file_name, 'w')
        print file_name
        self.handler.server.cur_file=file_name
        self.sendResponse(200)
        return 0
       
        
    def file_data(self):
	ip  = self.handler.client_address[0]
        len = int(self.handler.headers.get('Content-Length'))
        file_data=self.handler.rfile.read(len)
        print "Data " + file_data
        print "FILE NAME " + self.handler.server.cur_file
        f = open('/home/shardul/'+self.handler.server.cur_file,'a+')
        f.write(file_data + '\n')
        f.close()
        self.sendResponse(200)
        return 0

#Handler    
class MyHandler (BaseHTTPRequestHandler):

    def PreProcess(self):
		print (self.client_address, self.command, self.path, self.request_version, self.headers.headers)
		return 0

    def do_POST(self):
        try:
            if self.PreProcess():
                return
            p=POST_check(self)
            p.handle_req(self.path)
            return
        
        except IOError:
            self.send_error(404, 'File Not found %s' % self.path)
            
            
class metaTable():
    entry_list=[]
    count=0
    def add_entry(self, index, cur_file, cur_dir, size):
        self.entry_list[count][0]=index
        self.entry_list[count][1]=cur_dir
        self.entry_list[count][2]=cur_file
        self.entry_list[count][3]=size
        self.count=self.count+1

    def fetch_entry(self, index):
        value=self.entry_list.index(index)
        return entry_list[value:value+3]
    
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    table=metaTable()
    cur_file=''
    def set_var(self,value):
        ThreadingHTTPServer.p=value
    def get_var(self):
       print ThreadingHTTPServer.p
    pass

# Start
def main():
	try:
		server = ThreadingHTTPServer(('', 5080), MyHandler)
                server.set_var(10)
                server.get_var()
		print 'Started POST_check HttpServer.....'
		server.serve_forever()

	except KeyboardInterrupt:
		print '^C received, shuting down server'
		server.socket.close()

if __name__ == '__main__':
	main()
