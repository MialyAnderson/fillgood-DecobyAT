from sqlalchemy import desc, asc
from sqlalchemy.sql import func
from models import Session, Produit
import datetime

def ajouter_produit(titre, prix, description=None, categorie=None, image=None):
    """
    Ajoute un nouveau produit à la base de données
    
    Args:
        titre (str): Le nom du produit
        prix (float): Le prix du produit
        description (str, optional): La description du produit
        categorie (str, optional): La catégorie du produit
        image (str, optional): Le chemin vers l'image du produit
        
    Returns:
        Produit: L'objet produit créé
    """
    session = Session()
    nouveau_produit = Produit(
        titre=titre,
        prix=prix,
        description=description,
        categorie=categorie,
        image=image,
        date_publication=datetime.datetime.now()
    )
    
    try:
        session.add(nouveau_produit)
        session.commit()
        return nouveau_produit
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def obtenir_tous_produits(tri='recent'):
    """
    Récupère tous les produits de la base de données avec option de tri
    
    Args:
        tri (str): Option de tri ('recent', 'ancien', 'prix_asc', 'prix_desc')
    
    Returns:
        list: Liste de tous les produits
    """
    session = Session()
    try:
        query = session.query(Produit)
        
        # Application du tri
        if tri == 'recent':
            query = query.order_by(desc(Produit.date_publication))
        elif tri == 'ancien':
            query = query.order_by(asc(Produit.date_publication))
        elif tri == 'prix_asc':
            query = query.order_by(asc(Produit.prix))
        elif tri == 'prix_desc':
            query = query.order_by(desc(Produit.prix))
        
        produits = query.all()
        return produits
    finally:
        session.close()

def obtenir_produit_par_id(produit_id):
    """
    Récupère un produit par son ID
    
    Args:
        produit_id (int): L'ID du produit à récupérer
        
    Returns:
        Produit: Le produit trouvé ou None
    """
    session = Session()
    try:
        produit = session.query(Produit).filter(Produit.id == produit_id).first()
        return produit
    finally:
        session.close()

def rechercher_produits(terme_recherche, tri='recent'):
    """
    Recherche des produits par titre ou description avec option de tri
    
    Args:
        terme_recherche (str): Le terme à rechercher
        tri (str): Option de tri ('recent', 'ancien', 'prix_asc', 'prix_desc')
        
    Returns:
        list: Liste des produits correspondants
    """
    session = Session()
    try:
        # Recherche partielle avec l'opérateur LIKE
        terme = f"%{terme_recherche}%"
        query = session.query(Produit).filter(
            (Produit.titre.like(terme)) | 
            (Produit.description.like(terme))
        )
        
        # Application du tri
        if tri == 'recent':
            query = query.order_by(desc(Produit.date_publication))
        elif tri == 'ancien':
            query = query.order_by(asc(Produit.date_publication))
        elif tri == 'prix_asc':
            query = query.order_by(asc(Produit.prix))
        elif tri == 'prix_desc':
            query = query.order_by(desc(Produit.prix))
            
        produits = query.all()
        return produits
    finally:
        session.close()

def mettre_a_jour_produit(produit_id, **kwargs):
    """
    Met à jour un produit existant
    
    Args:
        produit_id (int): L'ID du produit à mettre à jour
        **kwargs: Les champs à mettre à jour (titre, prix, description, categorie, image)
        
    Returns:
        bool: True si la mise à jour a réussi, False sinon
    """
    session = Session()
    try:
        resultat = session.query(Produit).filter(Produit.id == produit_id).update(kwargs)
        session.commit()
        return resultat > 0
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def supprimer_produit(produit_id):
    """
    Supprime un produit de la base de données
    
    Args:
        produit_id (int): L'ID du produit à supprimer
        
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    session = Session()
    try:
        produit = session.query(Produit).filter(Produit.id == produit_id).first()
        if produit:
            session.delete(produit)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()