from models import Produit, Session, init_db
import datetime

# S'assurer que la base de données est initialisée
init_db()

# Créer une session
session = Session()

# Liste des produits à ajouter
produits = [
    {
        "titre": "Amigurumi Lapin",
        "prix": 25.00,
        "description": "Joli lapin en crochet fait main, parfait pour décorer ou comme cadeau.",
        "categorie": "Amigurumi",
        "image": "images/produits/lapin.jpg"  # Assurez-vous que cette image existe dans static/images/produits/
    },
    {
        "titre": "Couverture Bébé",
        "prix": 45.00,
        "description": "Couverture douce et chaude pour bébé, en coton biologique.",
        "categorie": "Bébé",
        "image": "images/produits/couverture.jpg"
    },
    {
        "titre": "Bonnet d'hiver",
        "prix": 18.50,
        "description": "Bonnet chaud et confortable pour l'hiver, disponible en plusieurs couleurs.",
        "categorie": "Vêtements",
        "image": "images/produits/bonnet.jpg"
    },
    {
        "titre": "Déco Murale Macramé",
        "prix": 39.90,
        "description": "Belle décoration murale en macramé pour apporter une touche bohème.",
        "categorie": "Décoration",
        "image": "images/produits/deco_murale.jpg"
    },
    {
        "titre": "Hochet Crochet",
        "prix": 15.00,
        "description": "Hochet en crochet pour bébé, doux et sans danger.",
        "categorie": "Bébé",
        "image": "images/produits/hochet.jpg"
    },
    {
        "titre": "Sac Cabas",
        "prix": 32.00,
        "description": "Sac cabas pratique et élégant, réalisé en fil de coton.",
        "categorie": "Accessoires",
        "image": "images/produits/sac.jpg"
    }
]

try:
    # Vérifier si les produits existent déjà (basé sur le titre)
    for produit_data in produits:
        existing_product = session.query(Produit).filter_by(titre=produit_data["titre"]).first()
        
        if existing_product:
            print(f"Le produit '{produit_data['titre']}' existe déjà dans la base de données.")
        else:
            # Créer un nouvel objet Produit
            nouveau_produit = Produit(
                titre=produit_data["titre"],
                prix=produit_data["prix"],
                description=produit_data["description"],
                categorie=produit_data["categorie"],
                image=produit_data["image"],
                date_publication=datetime.datetime.now()
            )
            
            # Ajouter à la session
            session.add(nouveau_produit)
            print(f"Produit '{produit_data['titre']}' ajouté avec succès.")
    
    # Commmit pour sauvegarder les changements
    session.commit()
    print("\nTous les produits ont été traités avec succès.")
    
except Exception as e:
    # En cas d'erreur, annuler les changements
    session.rollback()
    print(f"Une erreur s'est produite: {str(e)}")
    
finally:
    # Fermer la session
    session.close()