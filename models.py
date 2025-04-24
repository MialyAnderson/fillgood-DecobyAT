from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from base import Base  
from sqlalchemy.orm import sessionmaker
from models_user import User, create_admin_if_not_exists
import datetime

# Création de la base de données SQLite
engine = create_engine('sqlite:///fillgood.db', echo=True)
Session = sessionmaker(bind=engine)

# Définition du modèle Produit
class Produit(Base):
    __tablename__ = 'produits'
    
    id = Column(Integer, primary_key=True)
    titre = Column(String(100), nullable=False)
    prix = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    categorie = Column(String(50), nullable=True)
    image = Column(String(200), nullable=True)
    date_publication = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Produit(id={self.id}, titre='{self.titre}', prix={self.prix}, date={self.date_publication})>"

# Création des tables dans la base de données
def init_db():
    Base.metadata.create_all(engine)
    session = Session()                              
    create_admin_if_not_exists(session)              
    session.close()  

if __name__ == "__main__":
    # Initialisation de la base de données si ce script est exécuté directement
    init_db()
    print("Base de données initialisée avec succès.")