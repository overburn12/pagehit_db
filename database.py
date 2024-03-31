from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.orm import sessionmaker, declarative_base
import json
from datetime import datetime

Base = declarative_base()

class PageHit(Base):
    __tablename__ = 'page_hit'
    id = Column(Integer, primary_key=True)
    website_id = Column(String(50)) 
    page_url = Column(String(500))
    method = Column(String(10))  
    response_code = Column(Integer)
    visit_datetime = Column(DateTime, default=datetime.utcnow) 
    visitor_id = Column(String(100))
    referrer_url = Column(String(500))
    user_agent = Column(String(500))
    is_ssl = Column(Boolean) 

Index('idx_visit_datetime_website_id', PageHit.visit_datetime, PageHit.website_id)

engine = None

def init_db(db_uri):
    global engine
    engine = create_engine(db_uri, echo=False)
    Base.metadata.create_all(engine)


def validate_data(data):
    data_fields = data.keys()
    expected_fields = {
        'website_id': str,
        'page_url': str,
        'method': str,
        'response_code': int,
        'visit_datetime': datetime,
        'visitor_id': str,
        'referrer_url': str,
        'user_agent': str,
        'is_ssl': bool
    }

    for field in expected_fields:
        if field not in data_fields:
            #skip visit_datetime if not supplied, it has a default value
            if field == 'visit_datetime':
                continue
            return False, f'{field} is missing from data'

    for field in data_fields:
        if not isinstance(data[field], expected_fields[field]):
            return False, f"{field} has incorrect type, expected {expected_fields[field].__name__}"   
        
    return True, 'data verified'


def add(req_data):
    # Convert JSON to dictionary if necessary
    if isinstance(req_data, str):
        data = json.loads(req_data)
    else:
        data = req_data
    
    Session = sessionmaker(bind=engine)
    session = Session()

    page_hit = PageHit(**data)
    session.add(page_hit)
    session.commit()


def query(raw_text):
    Session = sessionmaker(bind=engine)
    session = Session()
    
    result = session.execute(text(raw_text))
    rows = result.fetchall()
    columns = result.keys()
    
    formatted_results = {
                'columns': list(columns),
                'rows': [dict(zip(columns, row)) for row in rows]
            }
    return formatted_results

def track_page(request, response):
    ##used to track self http activity, rather than the /create endpoint
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