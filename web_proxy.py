'''
COMP 360, Section 1, Fall 2016
Justin Kim
WebProxy is a proxy that takes in a GET Request from a client, and sends back
an HTTP response. The Proxy listens continuously until the user terminates using
control-break or control-c (depending on your machine)
'''


import socket
import sys
import threading


class WebProxy():

    def __init__(self, server_host, server_port):

        self.server_host = server_host
        self.server_port = server_port
        self.server_backlog = 1
        self.proxyCache = {}
        self.start()

    def start(self):
        # Initialize server socket on which to listen for connections
        try:
            server_sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind((self.server_host, self.server_port))
            server_sock.listen(self.server_backlog)
        except OSError as e:
            print('Unable to open socket: ', e)
            if server_sock:
                server_sock.close()
            sys.exit(1)

        # Wait for client connection
        while True:
            # Client has connected
            [client_conn, client_addr] = server_sock.accept()
            print('Client has connected with address: ', client_addr)
            # Create thread to serve client
            thread = threading.Thread(
                target=self.serve_content,
                args=(client_conn, client_addr))
            thread.start()
# serve_content deals with recieving data from the host and sending
# it to the client.

    def serve_content(self, client_conn, client_addr):
        print('Serving content to client with address', client_addr)

        # Receive data from client
        bin_data = client_conn.recv(4096)
        # Parse the GET request to be sent to web server
        bin_data = self.generalParse(bin_data)[1]
        host = self.generalParse(bin_data)[0]
        try:
            # This is when the GET request is sent to the webserver and returns
            # HTTP Response
            siteData = self.getSite(host, 80, bin_data)
            if siteData == 'ERROR: TRY AGAIN':  # In case getSite returns an error. Exits program
                client_conn.sendall(siteData.encode('utf-8'))
                client_conn.close()
                sys.exit(1)
        except OSError as e:
            client_conn.close()

        # Cache data is in the format (Response Code,Date,Last
        # Modified,HTTP Response)
        try:
            # Runs cacheData to sort out the data for the cache.
            cacheData = self.cacheData(siteData)
        except AttributeError as e:
            print('Error', e)
        # Displays the response code to the server.
        print('Response Code', self.cacheData(siteData)[0])

        # If response is not 304 Not Modified then cache.
        if self.statusReact(cacheData):
            # Pairs cacheData to the url in the proxy cache. In the format
            # (Url,Cache Data)
            self.proxyCache[host] = cacheData
        else:
            try:
                # If Response is 304, then send cached response to client.
                cacheItem = self.proxyCache[host]
                siteData = cacheItem[2]
            except KeyError as e:
                print('Invalid Host')
        try:
            # Send either cached or new http response from previous expression
            client_conn.sendall(siteData)
        except TypeError as e:
            errorMessage = 'Unable to connect to requeested host.Please Try again.'
            binError = errorMessage.encode('utf-8')
            client_conn.sendall(binError)
        client_conn.close()
        '''
		Get Site retrieves the HTTP response from the webserver. Takes in
		a host, port and request(GET REQUEST). Can return an error (which is handled by serve_content) or site data.
		It creates a new socket, that creates a TCP connection with the web server.
		'''

    def getSite(self, server_host, server_port, request):
        # Creates a socket
        try:
            toHostSocket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            toHostSocket.connect((server_host, server_port))
        except OSError as e:
            print('Cant connect to: ' + server_host	)
            return ('ERROR: TRY AGAIN')
        # Sends formatted and final GET Request to Web Server
        toHostSocket.sendall(request)
        fullSite = ''.encode('utf-8')  # emptyData
        while True:  # Loops to recieve all data from webserver
            site = toHostSocket.recv(4096)
            if not site:
                break
            fullSite = fullSite + site
        toHostSocket.close()
        return fullSite

    '''
   	cacheData sorts out the http response to separate the response Code #,
   	the date, and the Last Modified date.
   	'''

    def cacheData(self, data):
        try:
            decoded = data.decode('utf-8')
        except UnicodeDecodeError as e:
            print('Cant decode. Non UTF-8')
            return('', '', data)
        responseCode = decoded[9:(decoded.index('\r\n'))]
        date = ''

        if 'Last-Modified: ' in decoded:
            LastModS = decoded.index('Last-Modified: ')
            LastMod = decoded[LastModS + 15:(decoded.index('\r\n', LastModS))]
        if date == '' and 'Date:' in decoded:
            dateS = decoded.index('Date:')
            date = decoded[dateS + 6:(decoded.index('\r\n', dateS))]
        return (responseCode, date, data)

    def statusReact(self, cacheData):
        if cacheData[0] == '304 Not Modified':
            return False
        else:
            return True
    '''
	generalParse formats and sorts the GET request from the client.
	Checks for the web browser format and web_client.py format.
	takes in a GET Request and returns a url and the formated GET Request.
	'''

    def generalParse(self, bin_data):
        data = bin_data.decode('utf-8')
        path = ''
        if 'Keep-Alive' in data:
            data.replace('Connection: keep-alive', 'Connection: close')
        if 'GET' in data:
            getField = data[data.index('GET'):data.index('\r\n', 4)]
            if 'http://' in getField:
                hostname = getField[getField.index(
                    'http://') + 7:getField.index('/', 12)]
                path = getField[getField.index(
                    '/', getField.index('http://') + 7):]
                data = 'GET %s \r\nConnection: close\r\nHost: %s\r\n\r\n' % (
                    path, hostname)
                data.replace('http://', '', 1)
        hostS = data.index('Host: ') + 6	
        hostE = data.index('\r\n', hostS)
        host = data[hostS:hostE]
        if ((host + path) in self.proxyCache) and ('If-Modified-Since' not in data):
            ifMod = 'If-Modified-Since: %s\r\n\r\n' % (
                self.proxyCache[host][1])
            data = data[:data.index('\r\n\r\n') + 2] + ifMod
        data = data.encode('utf-8')
        return (host + path, data)

'''
main() runs the program. 
'''


def main():

    # Echo server socket parameters
    server_host = 'localhost'
    server_port = 50008

    # Parse command line parameters
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    # Create EchoServer object
    Proxy = WebProxy(server_host, server_port)

if __name__ == '__main__':
    main()
