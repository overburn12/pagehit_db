from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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

    data_fields = data.keys()
    for field, field_type in expected_fields.items():
        if field not in data_fields:
            #skip visit_datetime if not supplied, it has a default value
            if field == 'visit_datetime':
                continue
            return False, f'{field} is missing from data'
            
        if not isinstance(data[field], field_type):
            if field == 'visit_datetime' and data[field] is not None:
                return False, f'{field} has incorrect type, expected {field_type}'
        
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