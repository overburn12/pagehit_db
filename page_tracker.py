import requests, os
from dotenv import load_dotenv
from database import add
load_dotenv()

DB_URL = os.getenv('DB_URL')

def track_page(request, response):
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    is_ssl = request.headers.get('X-Forwarded-Proto', 'http') == 'https'
    data = {
        'website_id': 'admin.overburn.dev',
        'page_url': request.path,
        'response_code': response.status_code,
        'visitor_id': visitor_ip,
        'referrer_url': request.referrer or '',
        'user_agent': request.user_agent.string,
        'method': request.method,
        'is_ssl': is_ssl
    }

    add(data)