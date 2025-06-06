"""
WSGI entry point for cPanel Python application
"""
import sys
import os

# Add the application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def application(environ, start_response):
    """
    Basic WSGI application for cPanel
    This can be expanded to provide a web interface for the crawler
    """
    status = '200 OK'
    output = b'''
    <html>
    <head><title>QRM Chatbot Knowledge Base</title></head>
    <body>
        <h1>QRM Chatbot Knowledge Base Crawler</h1>
        <p>This is a backend service for crawling WooCommerce data.</p>
        <p>The crawler runs via cron jobs and stores data in MySQL and ChromaDB.</p>
        <hr>
        <p><strong>Note:</strong> This is not meant to be accessed via web browser.</p>
        <p>Use SSH or cron jobs to run: <code>python main.py --site-name store1</code></p>
    </body>
    </html>
    '''

    response_headers = [('Content-type', 'text/html'),
                       ('Content-Length', str(len(output)))]
    
    start_response(status, response_headers)
    return [output]

# For cPanel compatibility
wsgi = application