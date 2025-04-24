from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid
from base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='user')  # 'user' ou 'admin'
    profile_picture = Column(String(200), nullable=True)
    date_inscription = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __init__(self, username, email, password, role='user', profile_picture=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        self.profile_picture = profile_picture
    
    def set_password(self, password):
        """Génère un hash du mot de passe avec sel"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie si le mot de passe correspond au hash stocké"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Vérifie si l'utilisateur est un administrateur"""
        return self.role == 'admin'
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire (sans le hash du mot de passe)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'profile_picture': self.profile_picture,
            'date_inscription': self.date_inscription,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"

# Fonction pour créer un utilisateur admin si nécessaire
def create_admin_if_not_exists(session):
    """Crée un utilisateur admin s'il n'existe pas déjà"""
    admin = session.query(User).filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@fillgood.com',
            password='admin123',  # À changer dans un environnement de production !
            role='admin'
        )
        session.add(admin)
        session.commit()
        print("Utilisateur admin créé avec succès.")
    return admin