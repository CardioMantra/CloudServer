# Copyright (c) 2024 Kyryll Rubanyk
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import http.server
import socketserver
import ssl
import os
import json

#directory to download files
server_directory = "server_directory"

class FileServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/check_upload":
            #receive a list of client's files
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            print(data)
            client_files = json.loads(data.decode('utf-8'))
            
            # Extract the filenames and add corresponding .hea files
            for file in client_files[:]:  # Using a copy of the list
                if file.endswith('.dat'):
                    hea_file = file.replace('.dat', '.hea')
                    client_files.append(hea_file)
            
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
#    with socketserver.TCPServer(("", PORT), Handler) as httpd:
#        print("Server started at port", PORT)
#        httpd.serve_forever()

    httpd = socketserver.TCPServer(("", PORT), Handler)
    
    # Add SSL support
    httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="server_certs/ca_key.pem", certfile="server_certs/ca_cert.pem", server_side=True)

#SSL V2
    # Create an SSL context
#    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#    context.load_cert_chain(certfile="ca_cert.pem", keyfile="ca_key.pem")
    
    # Apply SSL context to the server socket
#    httpd.socket = context.wrap_socket(httpd.socket)
#end V2
    
    print("Server started at port", PORT)
    httpd.serve_forever()
