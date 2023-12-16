import time
from sqlalchemy import create_engine, Column, String, Integer, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from codelearn.base import PROJECT_DATABASE_URL

Base = declarative_base()

class ProjectModel(Base):
    __tablename__ = 'projects'

    id = Column(String, primary_key=True)
    repo_url = Column(String, nullable=False)
    local_dir = Column(String, nullable=False)
    last_updated = Column(Integer, default=datetime.now().timestamp())

engine = create_engine(PROJECT_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

def get_project(project_id=None, repo_url=None, local_dir=None):
    session = SessionLocal()
    
    filters = []
    if project_id:
        filters.append(ProjectModel.id == project_id)
    if repo_url:
        filters.append(ProjectModel.repo_url == repo_url)
    if local_dir:
        filters.append(ProjectModel.local_dir == local_dir)

    if not filters:
        session.close()
        raise ValueError("At least one identifying field must be provided")

    project = session.query(ProjectModel).filter(or_(*filters)).first()
    print(f"db in: {project}")
    session.close()
    return project

def get_project_by_id(project_id):
    session = SessionLocal()
    project = session.query(ProjectModel).filter_by(id=project_id).first()
    session.close()
    return project


def get_project_by_repo(repo_url):
    session = SessionLocal()
    project = session.query(ProjectModel).filter_by(repo_url=repo_url).first()
    session.close()
    return project


def insert_or_update_project(project_id, repo_url, local_dir):
    
    session = SessionLocal()
    project = session.query(ProjectModel).filter_by(id=project_id).first()

    if not project:
        new_project = ProjectModel(
            id=project_id,
            repo_url=repo_url,
            local_dir=local_dir,
        )
        session.add(new_project)
    else:
        project.last_updated = datetime.utcnow()

    session.commit()
    session.close()
