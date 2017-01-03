# WebClient-WebProxy
Simple Web Client and Proxy

##Web Client
Web client that connects to a web Proxy, sends a HTTP GET request,
            then recieves back an HTTP response. It then reads the response and terminates. 

To run the client: `python3 web_client.py`
   Client will then prompt an address.
            
##Web Proxy
WebProxy is a proxy that takes in a GET Request from a client, and sends back
           an HTTP response. The Proxy listens continuously until the user terminates using
           control-break or control-c (depending on your machine)
           
To run the proxy: `python3 web_proxy.py`




#Usage:
For browser usage:
Run the web_proxy.py file. 
Set up browser to listen on 'localhost' on port 50008
Type into the browser any http url. 

For web_client.py usage:
Run the web_proxy.py file. 
Run the web_client.py file.
The client will ask you for a url.
Input a url with the format `http://www.[domain name].[domain suffix]/[Path...]`
The proxy will return an HTTP Response back to the client. 

            
