# Copyright (c) 2023 Kyryll Rubanyk
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import http.server
import socketserver
import os
import json

server_directory = "server_directory"

class FileServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/check_upload":
            #receive a list of client's files
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            print(data)
            client_files = json.loads(data.decode('utf-8'))
            #get a list of server files
            server_files = os.listdir(server_directory)
            #create a list of new files to download from client
            files_to_download = [filename for filename in client_files if filename not in server_files]
            #send response with the list of files to download
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(files_to_download).encode('utf-8'))
            print("done!")
        else:
            #download files
            self.handle_download()

    def handle_download(self):
        #get a content size
        content_length = int(self.headers['Content-Length'])
        #get raw file content
        file_content = self.rfile.read(content_length)
        #get filename
        filename = self.headers.get('X-File-Name', 'unknown.bin')
        print("file ", filename, " downloaded succesfully")
        #write content to the file with the appropriate filename
        with open(os.path.join(server_directory, filename), 'wb') as f:
            f.write(file_content)
        #send response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'File downloaded and saved successfully!')

if __name__ == "__main__":
    PORT = 8000
    Handler = FileServerHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Server started at port", PORT)
        httpd.serve_forever()
