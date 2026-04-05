import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

Base = declarative_base()

class App(Base):
    __tablename__ = 'apps'
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, nullable=False)
    name = Column(String)
    pings = relationship("Ping", back_populates="app")

class Ping(Base):
    __tablename__ = 'pings'
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey('apps.id'))
    timestamp = Column(DateTime, default=datetime.now, index=True)
    stats = Column(JSON)
    app = relationship("App", back_populates="pings")

class DatabaseManager:
    def __init__(self, settings):
        self.settings = settings
        self.config = settings.postgresql
        self.engine = None
        self.Session = None

        if settings.use_postgresql:
            self.setup_db()

    def setup_db(self):
        host = self.config.get('host')
        port = self.config.get('port')
        user = self.config.get('user')
        password = self.config.get('password')
        dbname = self.config.get('database')

        # 1. Create database if not exists
        try:
            self._create_database_if_not_exists(host, port, user, password, dbname)
        except Exception as e:
            print(f"Error creating database: {e}")

        # 2. Setup SQLAlchemy
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _create_database_if_not_exists(self, host, port, user, password, dbname):
        # Connect to 'postgres' to create the new database
        con = psycopg2.connect(dbname='postgres', user=user, host=host, password=password, port=port)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE {dbname}')
        cur.close()
        con.close()

    def get_session(self):
        if not self.Session:
            return None
        return self.Session()

    def save_ping(self, app_slug, stats, timestamp=None):
        session = self.get_session()
        if not session:
            return

        try:
            # Get or create app
            app = session.query(App).filter_by(slug=app_slug).first()
            if not app:
                app = App(slug=app_slug, name=app_slug.replace('-', ' ').title())
                session.add(app)
                session.commit()

            ping = Ping(app_id=app.id, stats=stats)
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                ping.timestamp = timestamp
            
            session.add(ping)
            session.commit()
        except Exception as e:
            print(f"Error saving ping to Postgres: {e}")
            session.rollback()
        finally:
            session.close()

    def get_pings(self, app_slug, start_time, end_time=None):
        session = self.get_session()
        if not session:
            return []

        try:
            query = session.query(Ping).join(App).filter(App.slug == app_slug)
            query = query.filter(Ping.timestamp >= start_time)
            if end_time:
                query = query.filter(Ping.timestamp <= end_time)
            
            pings = query.order_by(Ping.timestamp.asc()).all()
            return pings
        except Exception as e:
            print(f"Error fetching pings from Postgres: {e}")
            return []
        finally:
            session.close()

    def get_latest_ping(self, app_slug):
        session = self.get_session()
        if not session:
            return None

        try:
            ping = session.query(Ping).join(App).filter(App.slug == app_slug).order_by(Ping.timestamp.desc()).first()
            return ping
        except Exception as e:
            print(f"Error fetching latest ping from Postgres: {e}")
            return None
        finally:
            session.close()
