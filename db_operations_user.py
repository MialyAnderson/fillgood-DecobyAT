from sqlalchemy.exc import IntegrityError
from models import Session
from models_user import User

def ajouter_utilisateur(username, email, password, role='user', profile_picture=None):
    """
    Ajoute un nouvel utilisateur
    
    Args:
        username (str): Nom d'utilisateur
        email (str): Email de l'utilisateur
        password (str): Mot de passe (sera haché)
        role (str, optional): Rôle ('user' ou 'admin')
        profile_picture (str, optional): Chemin vers l'image de profil
    
    Returns:
        tuple: (User, str) - L'objet utilisateur créé et un message, ou (None, str) en cas d'erreur
    """
    session = Session()
    
    # Vérifier si l'utilisateur ou l'email existe déjà
    existing_user = session.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        if existing_user.username == username:
            return None, "Ce nom d'utilisateur est déjà pris."
        else:
            return None, "Cet email est déjà utilisé."
    
    try:
        nouvel_utilisateur = User(
            username=username,
            email=email,
            password=password,
            role=role,
            profile_picture=profile_picture
        )
        
        session.add(nouvel_utilisateur)
        session.commit()
        return nouvel_utilisateur, "Utilisateur créé avec succès."
    except IntegrityError:
        session.rollback()
        return None, "Erreur d'intégrité des données."
    except Exception as e:
        session.rollback()
        return None, f"Erreur lors de la création de l'utilisateur: {str(e)}"
    finally:
        session.close()

def authentifier_utilisateur(identifiant, password):
    """
    Authentifie un utilisateur par nom d'utilisateur ou email
    
    Args:
        identifiant (str): Nom d'utilisateur ou email
        password (str): Mot de passe en clair
    
    Returns:
        User ou None: L'utilisateur si authentifié, sinon None
    """
    session = Session()
    try:
        # Recherche par nom d'utilisateur ou email
        utilisateur = session.query(User).filter(
            (User.username == identifiant) | (User.email == identifiant)
        ).first()
        
        if utilisateur and utilisateur.check_password(password):
            return utilisateur
        return None
    finally:
        session.close()

def obtenir_utilisateur_par_id(user_id):
    """
    Récupère un utilisateur par son ID
    
    Args:
        user_id (int): ID de l'utilisateur
    
    Returns:
        User ou None: L'utilisateur trouvé ou None
    """
    session = Session()
    try:
        utilisateur = session.query(User).filter(User.id == user_id).first()
        return utilisateur
    finally:
        session.close()

def mettre_a_jour_utilisateur(user_id, **kwargs):
    """
    Met à jour un utilisateur existant
    
    Args:
        user_id (int): ID de l'utilisateur
        **kwargs: Champs à mettre à jour (username, email, profile_picture, role, is_active)
    
    Returns:
        bool: True si la mise à jour a réussi, False sinon
    """
    session = Session()
    try:
        # Si le mot de passe est fourni, il faut le hacher
        if 'password' in kwargs:
            utilisateur = session.query(User).filter(User.id == user_id).first()
            if utilisateur:
                utilisateur.set_password(kwargs.pop('password'))
                session.add(utilisateur)
        
        # Mettre à jour les autres champs
        if kwargs:
            resultat = session.query(User).filter(User.id == user_id).update(kwargs)
            session.commit()
            return resultat > 0
        else:
            session.commit()
            return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def supprimer_utilisateur(user_id):
    """
    Supprime un utilisateur de la base de données
    
    Args:
        user_id (int): ID de l'utilisateur à supprimer
    
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    session = Session()
    try:
        utilisateur = session.query(User).filter(User.id == user_id).first()
        if utilisateur:
            session.delete(utilisateur)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def rechercher_utilisateurs(terme_recherche):
    """
    Recherche des utilisateurs par nom d'utilisateur ou email
    
    Args:
        terme_recherche (str): Le terme à rechercher
    
    Returns:
        list: Liste des utilisateurs correspondants
    """
    session = Session()
    try:
        terme = f"%{terme_recherche}%"
        utilisateurs = session.query(User).filter(
            (User.username.like(terme)) | 
            (User.email.like(terme))
        ).all()
        return utilisateurs
    finally:
        session.close()