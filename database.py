from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Index
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import json, shutil, os
from datetime import datetime

Base = declarative_base()

class PageHit(Base):
    __tablename__ = 'page_hit'
    id = Column(Integer, primary_key=True)
    visit_datetime = Column(DateTime) 
    visitor_id = Column(String(100))
    scheme = Column(String(5)) 
    website_id = Column(String(100)) 
    page_url = Column(String(100))
    method = Column(String(10))  
    response_code = Column(Integer)
    bytes_sent = Column(Integer)
    referrer_url = Column(String(500))
    user_agent = Column(String(500))

Index('idx_visit_datetime_website_id', PageHit.visit_datetime, PageHit.website_id)

engine = None

def init_db(db_uri):
    global engine
    engine = create_engine(db_uri, echo=False)
    Base.metadata.create_all(engine)


def query(raw_text):
    Session = sessionmaker(bind=engine)
    session = Session()
    
    result = session.execute(text(raw_text))
    rows = result.fetchall()
    columns = result.keys()
    session.close()

    formatted_results = {
                'columns': list(columns),
                'rows': [dict(zip(columns, row)) for row in rows]
            }
    return formatted_results


def parse_log_file(log_path):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with open(log_path, 'r+') as file:
            log_entries = file.readlines()
            file.truncate(0)
        if log_entries:  # Check if there are entries to process
            for line in log_entries:
                try:
                    log_entry = json.loads(line)
                    page_hit = PageHit(
                        visit_datetime=datetime.strptime(log_entry['time_local'], '%d/%b/%Y:%H:%M:%S %z'),
                        visitor_id=log_entry['visitor_id'],
                        scheme=log_entry['scheme'],
                        website_id=log_entry['website_id'],
                        page_url=log_entry['page_url'],
                        method=log_entry['method'],
                        response_code=int(log_entry['response_code']),
                        bytes_sent=int(log_entry['bytes_sent']),
                        referrer_url=log_entry['referrer_url'],
                        user_agent=log_entry['user_agent']
                    )
                    session.add(page_hit)
                except Exception as e:
                    print(f"Error processing line: {e}")
            session.commit()
    except IOError as e:
        print(f"Failed to open or read file {log_path}: {e}")
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
    finally:
        session.close()


def rotate_log_file(from_path, to_path):
    shutil.copy2(from_path, to_path)
    with open(from_path, 'r+') as file:
        file.truncate(0)

def append_log(from_path, to_path):
    with open(from_path, 'r') as file_read:
        content = file_read.read()  
    with open(to_path, 'a') as file_append:
        file_append.write(content)  

def cleanup(log_path):
    os.remove(log_path)