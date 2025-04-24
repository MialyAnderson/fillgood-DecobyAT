
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
import os
from werkzeug.utils import secure_filename
from sqlalchemy import desc
from models import Session as DbSession
from models import init_db
from models_user import User, create_admin_if_not_exists
from db_operations import (
    ajouter_produit, 
    obtenir_tous_produits, 
    obtenir_produit_par_id, 
    mettre_a_jour_produit, 
    supprimer_produit,
    rechercher_produits,
    #obtenir_produits_par_categorie
)

from db_operations_user import (
    ajouter_utilisateur,
    authentifier_utilisateur,
    obtenir_utilisateur_par_id,
    mettre_a_jour_utilisateur,
    supprimer_utilisateur
)

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = 'fillgood_secret_key'  # Clé pour les sessions et les messages flash

# Configuration pour le téléchargement d'images
UPLOAD_FOLDER = 'static/images/produits'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Vérification de l'extension de fichier
def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = obtenir_utilisateur_par_id(user_id)

# Routes pour la partie client
@app.route('/')
def index():
    # Récupérer l'option de tri depuis les paramètres de l'URL
    tri = request.args.get('tri', 'recent')
    
    # Récupérer les produits avec l'option de tri
    produits = obtenir_tous_produits(tri=tri)
    
    return render_template('index.html', produits=produits, tri=tri)

@app.route('/produit/<int:produit_id>')
def detail_produit(produit_id):
    produit = obtenir_produit_par_id(produit_id)
    if produit:
        return render_template('detail_produit.html', produit=produit)
    flash('Produit non trouvé', 'error')
    return redirect(url_for('index'))

@app.route('/recherche')
def recherche():
    terme = request.args.get('q', '')
    tri = request.args.get('tri', 'recent')
    
    if terme:
        produits = rechercher_produits(terme, tri=tri)
    else:
        produits = []
    
    return render_template('resultats_recherche.html', produits=produits, terme=terme, tri=tri)

@app.route('/ajouter-produit', methods=['GET', 'POST'])
def ajouter_produit_route():
    if request.method == 'POST':
        titre = request.form.get('titre')
        prix = float(request.form.get('prix', 0))
        description = request.form.get('description')
        categorie = request.form.get('categorie')
        
        # Gestion de l'image
        image_path = None
        if 'image' in request.files:
            fichier = request.files['image']
            if fichier and allowed_file(fichier.filename):
                filename = secure_filename(fichier.filename)
                
                # Création du dossier s'il n'existe pas
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Enregistrement du fichier
                image_path = f'images/produits/{filename}'
                fichier.save(os.path.join('static', image_path))
        
        # Ajout du produit
        try:
            nouveau_produit = ajouter_produit(titre, prix, description, categorie, image_path)
            flash('Produit ajouté avec succès!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout du produit: {str(e)}', 'error')
    
    return render_template('ajouter_produit.html')

@app.route('/modifier-produit/<int:produit_id>', methods=['GET', 'POST'])
def modifier_produit_route(produit_id):
    produit = obtenir_produit_par_id(produit_id)
    if not produit:
        flash('Produit non trouvé', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        updates = {
            'titre': request.form.get('titre'),
            'prix': float(request.form.get('prix', 0)),
            'description': request.form.get('description'),
            'categorie': request.form.get('categorie')
        }
        
        # Gestion de l'image
        if 'image' in request.files and request.files['image'].filename:
            fichier = request.files['image']
            if allowed_file(fichier.filename):
                filename = secure_filename(fichier.filename)
                
                # Création du dossier s'il n'existe pas
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Enregistrement du fichier
                updates['image'] = f'images/produits/{filename}'
                fichier.save(os.path.join('static', updates['image']))
        
        # Mise à jour du produit
        try:
            mettre_a_jour_produit(produit_id, **updates)
            flash('Produit mis à jour avec succès!', 'success')
            return redirect(url_for('detail_produit', produit_id=produit_id))
        except Exception as e:
            flash(f'Erreur lors de la mise à jour du produit: {str(e)}', 'error')
    
    return render_template('modifier_produit.html', produit=produit)

@app.route('/supprimer-produit/<int:produit_id>', methods=['POST'])
def supprimer_produit_route(produit_id):
    try:
        success = supprimer_produit(produit_id)
        if success:
            flash('Produit supprimé avec succès!', 'success')
        else:
            flash('Produit non trouvé', 'error')
    except Exception as e:
        flash(f'Erreur lors de la suppression du produit: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    # Si l'utilisateur est déjà connecté, rediriger vers le profil
    if session.get('user_id'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        identifiant = request.form['identifiant']
        password = request.form['password']
        
        # Authentifier l'utilisateur
        user = authentifier_utilisateur(identifiant, password)
        
        if user:
            # Enregistrer l'utilisateur dans la session
            session.clear()
            session['user_id'] = user.id
            flash(f"Bienvenue, {user.username}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Identifiant ou mot de passe incorrect.", "error")
    
    return render_template('connexion.html')

@app.route('/inscription', methods=['POST'])
def inscription():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    # Vérifier que les mots de passe correspondent
    if password != confirm_password:
        flash("Les mots de passe ne correspondent pas.", "error")
        return redirect(url_for('connexion'))
    
    # Gérer la photo de profil
    profile_picture = None
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and file.filename and allowed_file(file.filename, {'jpg', 'jpeg', 'png', 'gif'}):
            filename = secure_filename(file.filename)
            profile_pic_path = f'images/profiles/{filename}'
            file.save(os.path.join('static', profile_pic_path))
            profile_picture = profile_pic_path
    
    # Ajouter l'utilisateur
    user, message = ajouter_utilisateur(username, email, password, profile_picture=profile_picture)
    
    if user:
        flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('connexion'))
    else:
        flash(message, "error")
        return redirect(url_for('connexion'))

@app.route('/deconnexion', methods=['POST'])
def deconnexion():
    session.clear()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for('index'))

# Ajoutez cette route à votre fichier index.py
@app.route('/profil')
def profil():
    if not session.get('user_id'):
        flash("Vous devez être connecté pour accéder à cette page.", "error")
        return redirect(url_for('connexion'))
    
    user = obtenir_utilisateur_par_id(session.get('user_id'))
    if not user:
        session.clear()
        flash("Utilisateur non trouvé. Veuillez vous reconnecter.", "error")
        return redirect(url_for('connexion'))
    
    # Pour les admins, récupérer tous les utilisateurs
    all_users = None
    if user.is_admin():
        db_session = DbSession()
        try:
            all_users = db_session.query(User).order_by(desc(User.date_inscription)).all()
        finally:
            db_session.close()
    
    return render_template('profil.html', user=user, all_users=all_users)

@app.route('/modifier-profil-form')
def modifier_profil_form():
    if not session.get('user_id'):
        flash("Vous devez être connecté pour accéder à cette page.", "error")
        return redirect(url_for('connexion'))
    
    user = obtenir_utilisateur_par_id(session.get('user_id'))
    if not user:
        session.clear()
        flash("Utilisateur non trouvé. Veuillez vous reconnecter.", "error")
        return redirect(url_for('connexion'))
    
    return render_template('modifier_profil.html', user=user)

@app.route('/modifier-profil', methods=['POST'])
def modifier_profil():
    if not session.get('user_id'):
        flash("Vous devez être connecté pour effectuer cette action.", "error")
        return redirect(url_for('connexion'))
    
    user = obtenir_utilisateur_par_id(session.get('user_id'))
    if not user:
        session.clear()
        flash("Utilisateur non trouvé. Veuillez vous reconnecter.", "error")
        return redirect(url_for('connexion'))
    
    # Récupérer les données du formulaire
    username = request.form.get('username')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Vérifier le mot de passe actuel
    if not user.check_password(current_password):
        flash("Mot de passe actuel incorrect.", "error")
        return redirect(url_for('modifier_profil_form'))
    
    # Vérifier si le nom d'utilisateur ou l'email est déjà utilisé
    db_session = DbSession()
    try:
        existing_user = db_session.query(User).filter(
            ((User.username == username) | (User.email == email)) & 
            (User.id != user.id)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                flash("Ce nom d'utilisateur est déjà pris.", "error")
            else:
                flash("Cet email est déjà utilisé.", "error")
            return redirect(url_for('modifier_profil_form'))
    finally:
        db_session.close()
    
    # Préparer les mises à jour
    updates = {
        'username': username,
        'email': email
    }
    
    # Gérer la photo de profil
    if 'profile_picture' in request.files and request.files['profile_picture'].filename:
        file = request.files['profile_picture']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            profile_pic_path = f'images/profiles/{filename}'
            
            # Création du dossier si nécessaire
            os.makedirs('static/images/profiles', exist_ok=True)
            
            file.save(os.path.join('static', profile_pic_path))
            updates['profile_picture'] = profile_pic_path
    
    # Gérer le changement de mot de passe si fourni
    if new_password:
        if new_password != confirm_password:
            flash("Les nouveaux mots de passe ne correspondent pas.", "error")
            return redirect(url_for('modifier_profil_form'))
        
        # Mise à jour du mot de passe
        db_session = DbSession()
        try:
            user_db = db_session.query(User).get(user.id)
            user_db.set_password(new_password)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            flash(f"Erreur lors du changement de mot de passe: {str(e)}", "error")
            return redirect(url_for('modifier_profil_form'))
        finally:
            db_session.close()
    
    # Mettre à jour les autres informations du profil
    try:
        mettre_a_jour_utilisateur(user.id, **updates)
        flash("Profil mis à jour avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de la mise à jour du profil: {str(e)}", "error")
    
    return redirect(url_for('profil'))

@app.route('/supprimer-mon-compte', methods=['POST'])
def supprimer_mon_compte():
    if not session.get('user_id'):
        flash("Vous devez être connecté pour effectuer cette action.", "error")
        return redirect(url_for('connexion'))
    
    user_id = session.get('user_id')
    
    try:
        success = supprimer_utilisateur(user_id)
        if success:
            session.clear()
            flash("Votre compte a été supprimé avec succès.", "success")
            return redirect(url_for('index'))
        else:
            flash("Une erreur est survenue lors de la suppression de votre compte.", "error")
    except Exception as e:
        flash(f"Erreur lors de la suppression du compte: {str(e)}", "error")
    
    return redirect(url_for('profil'))