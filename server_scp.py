#!/usr/bin/python

# Client side command to communicate to this server
# curl -d @ssh.py "http://<IP>:<port>/put_ssh_key/"

import string,os,errno, uuid
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from SocketServer import ThreadingMixIn

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

        print "handle_post_request" + operation
        
        if operation == 'file_data':
            self.file_data()
            
        if operation == 'file_end':
            self.file_end()

        if operation == 'file':
            self.file()

        if operation == 'dir':
            self.dir()

        if operation == 'dir_end':
            self.dir_end()

        if operation == 'time':
            self.time()
            
        if operation == 'initiate':
           self.initiate()

    def initiate(self):
        len = int(self.handler.headers.get('Content-Length'))
        base_dir=self.handler.rfile.read(len)
        id1=uuid.uuid4()        
        try:
            os.makedirs(base_dir)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        print 'Base Dir is ' ,base_dir
        idd=str(int(id1))
#        print self.handler.server.table.entry_list[0]        
        self.handler.server.table.add_entry(idd, '', '', 0, 0666, '', '', base_dir)
        print self.handler.server.table.entry_list[0]        
        self.handler.wfile.write(int(id1))
        self.sendResponse(200)
        
    def dir(self):
        len = int(self.handler.headers.get('Content-Length'))
        temp=self.handler.rfile.read(len)
        (tmp, ignore, temp) = temp.partition(' ')
        (index, ignore, tmp) = tmp.partition(':')        
        (tmp, ignore, temp) = temp.partition(' ')
        mode=int(tmp)
        (tmp, ignore, temp) = temp.partition(' ')
        size=int(tmp)
        (tmp, ignore, temp) = temp.partition(' ')
        base_dir=self.handler.server.table.get_value(index,7)
        dir_name=tmp
        try:
            os.makedirs(base_dir + dir_name, mode)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        self.handler.server.table.change_entry_field(index,1,dir_name)
        print self.handler.server.table.entry_list[0]
        self.sendResponse(200)
        return 0
    
    def time(self):
        len = int(self.handler.headers.get('Content-Length'))
        temp=self.handler.rfile.read(len)
        (tmp, ignore, temp) = temp.partition(' ')
        (index, ignore, tmp) = tmp.partition(':')        
        (tmp, ignore, temp) = temp.partition(' ')
        atime=int(tmp)
        self.handler.server.table.change_entry_field(index,5,atime)
        (tmp, ignore, temp) = temp.partition(' ')
        (tmp, ignore, temp) = temp.partition(' ')
        mtime=tmp
        self.handler.server.table.change_entry_field(index,6,mtime)        
        print "Time", atime, "   ", mtime
        return 0
        
    def file(self):
        len = int(self.handler.headers.get('Content-Length'))
        temp=self.handler.rfile.read(len)
        print temp
        (tmp, ignore, temp) = temp.partition(' ')
        (index, ignore, tmp) = tmp.partition(':')
        print "Aheroa", index
        (tmp, ignore, temp) = temp.partition(' ')
        mode=int(tmp)
        (tmp, ignore, temp) = temp.partition(' ')
        size=int(tmp)
        (tmp, ignore, temp) = temp.partition(' ')
        file_name=tmp
        print self.handler.server.table.entry_list[0]
        print 'File ' + file_name
        print 'Mode ' , mode
        print 'Size ' , size
        base_dir=self.handler.server.table.get_value(index,7)        
        dir_name=self.handler.server.table.get_value(index,1)
        print 'Full Path' ,base_dir + dir_name + '/' + file_name
        f=open(base_dir + dir_name + '/' + file_name, 'w')
        print file_name
        f.close()
        self.handler.server.table.change_entry_field(index, 2, file_name)
        self.handler.server.table.change_entry_field(index, 3, size)
        self.sendResponse(200)
        return 0
       
    def file_end(self):
        len = int(self.handler.headers.get('Content-Length'))
        index=self.handler.rfile.read(len)
        base_dir=self.handler.server.table.get_value(index,7)
        trunc=self.handler.server.table.get_value(index,3)
        dir_name=self.handler.server.table.get_value(index,1)
        file_name=self.handler.server.table.get_value(index,2)
        print "Last truncate " , trunc 
        f=open(base_dir+ dir_name + '/' + file_name,'a+')
        f.truncate(trunc)
        atime=int(self.handler.server.table.get_value(index,5))
        mtime=int(self.handler.server.table.get_value(index,6))
        f.close()
        os.utime(base_dir + dir_name + '/' + file_name,(atime,mtime))
        self.sendResponse(200)
        return 0
        
    def file_data(self):

	ip  = self.handler.client_address[0]
        len = int(self.handler.headers.get('Content-Length'))
        file_data=self.handler.rfile.read(len)
        (index, ignore, file_data) = file_data.partition(':')
        base_dir=self.handler.server.table.get_value(index,7)        
        dir_name=self.handler.server.table.get_value(index,1)
        file_name=self.handler.server.table.get_value(index,2)
        print 'File_data Full path', base_dir + dir_name + '/' + file_name 
        f=open(base_dir + dir_name + '/' + file_name,'a+')
        f.write(file_data)
        f.close()
        self.sendResponse(200)
        return 0

    def dir_end(self):
        len = int(self.handler.headers.get('Content-Length'))
        index=self.handler.rfile.read(len)
        
        base_dir=self.handler.server.table.get_value(index,7)        
        dir_name=self.handler.server.table.get_value(index,1)
        dir_name=dir_name.rsplit('/',1)[0]
        self.handler.server.table.change_entry_field(index,1,dir_name)        
        print "New Dir" + dir_name
        atime=int(self.handler.server.table.get_value(index,5))
        mtime=int(self.handler.server.table.get_value(index,6))
        os.utime(base_dir + dir_name ,(atime,mtime))
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
    def add_entry(self, index, cur_dir, cur_file, size, mode, atime, mtime, base_dir):
        self.entry_list.append([index, cur_dir, cur_file, size, mode, atime, mtime, base_dir])

    def change_entry_field(self, index, value_key, value):
        list_len= len(self.entry_list)
        print list_len
        for i in range(0,list_len):
            if self.entry_list[i][0]==index:
                print 'SUCCESS'
                self.entry_list[i][value_key]=value
                return 0
        
    def get_value(self, index, value_key):
        list_len= len(self.entry_list)
        print list_len
        for i in range(0,list_len):
            if self.entry_list[i][0]==index:
                print 'SUCCESS'
                return self.entry_list[i][value_key]
#TODO : Handle case of failure            
        return ''
    
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
		print 'Started POST_check HttpServer.....'
		server.serve_forever()

	except KeyboardInterrupt:
		print '^C received, shuting down server'
		server.socket.close()

if __name__ == '__main__':
	main()
