'''
COMP 360, Section 1, Fall 2016
Justin Kim
Web client that connects to a web Proxy, sends a HTTP GET request,
then recieves back an HTTP response. It then reads the response and terminates. 
'''

import socket
import sys


class WebClient():

    def __init__(self, server_host, server_port, request):
        self.start(server_host, server_port, request)

    def start(self, server_host, server_port, request):
        # Tries to connect to proxy. Prints exception and closes
        # process if it fails
        try:
            server_sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            server_sock.connect((server_host, server_port))
        except OSError as e:
            print('Unable to connect to socket: ', e)
            if server_sock:
                server_sock.close()
            sys.exit(1)
        # Encodes the Request
        bin_request = request.encode('utf-8')
        # Sends encoded request to the proxy
        server_sock.sendall(bin_request)
        # Recieve HTTP response back from proxy
        Webdata = ''.encode('utf-8')  # Empty Data
        while True: #Loop Recieve until all data has been recieved. 
            data = server_sock.recv(4096)
            if not data:
                break
            Webdata = Webdata + data
        print('Client has recieved:', Webdata) #Read data recieved from proxy.
        server_sock.close()
        sys.exit(1)# Close web_client
'''
formatGet() takes in the url passed into the client by the user, and 
formats the url into the GET response required by the proxy to be
sent to the host
'''


def formatGet(url):
    try:
        DomAddEnd = url.index('/')
        host = url[:DomAddEnd]
        path = url[DomAddEnd:]
        return 'GET %s HTTP/1.1\r\nConnection: close\r\nHost: %s\r\n\r\n' % (path, host) #If there is a path
    except ValueError as e:
        return 'GET / HTTP/1.1\r\nConnection: close\r\nHost: %s\r\n\r\n' % (url) #If there is no path


def main():
    url = ''
    # While loop asks user for correctly formated URL (with http:// included)
    while (url[0:7] != 'http://'):
        url = input(
            'Please enter a URL address (format http://www.[Domain].[Domain Suffix]/[Path...])\n')
    url = url[7:]  # Remove http prefix for formatGet() to work
    request = formatGet(url)
    # Create WebClient object
    # Proxy is always listening
    client = WebClient('localhost', 50008, request)
    # at this address
if __name__ == '__main__':
	while True:
   		 main()
   		 choice = input('Would you like to enter another URL? Y for Yes and N for No')
   		 if choice == N:
   		 	break
