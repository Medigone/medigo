# -*- coding: utf-8 -*-
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, nowdate, add_days, now
from frappe.model.document import Document

class Prescripteurs(Document):
    def before_insert(self):
        """
        Assigne automatiquement la date de création au champ 'Date Création'.
        """
        if not self.date_creation:
            self.date_creation = self.creation

    def validate(self):
        """
        Convertit automatiquement les champs en majuscules avant la sauvegarde.
        """
        if self.nom_prescripteur:
            self.nom_prescripteur = self.nom_prescripteur.upper()

        if self.prenom_prescripteur:
            self.prenom_prescripteur = self.prenom_prescripteur.upper()

        if self.nom_complet_prescripteur:
            self.nom_complet_prescripteur = self.nom_complet_prescripteur.upper()

    def before_save(self):
        """
        Synchronise l'utilisateur associé lors de la modification de l'email.
        """
        sync_user_with_email(self)

    def on_update(self):
        """
        Met à jour le statut et la date de dernière interaction après la sauvegarde.
        """
        self.update_status_and_date()

    def update_status_and_date(self):
        """
        Met à jour les champs `status` et `date_derniere_interaction` du prescripteur.
        """
        # Calcul de la date limite à 90 jours
        date_limite_90_jours = getdate(add_days(nowdate(), -90))

        # Récupération de la dernière interaction
        derniere_date = self.get_last_interaction_date()

        status = self.status  # Sauvegarde de l'ancien statut pour comparaison

        if derniere_date:
            self.date_derniere_interaction = derniere_date
            if derniere_date >= date_limite_90_jours:
                status = "Engagé"
            else:
                status = "Inactif"
        else:
            self.date_derniere_interaction = None
            if self.status != "Nouveau":
                status = "Non engagé"

        # Met à jour le statut si nécessaire
        if self.status != status:
            self.status = status

    def get_last_interaction_date(self):
        """
        Retourne la dernière date d'interaction du prescripteur.
        """
        result = frappe.db.sql("""
            SELECT MAX(date) AS derniere_date
            FROM (
                SELECT date FROM `tabVisite Prescripteur` WHERE prescripteur = %s
                UNION ALL
                SELECT date FROM `tabVisite Digitale` WHERE prescripteur = %s
            ) AS visites
        """, (self.name, self.name), as_dict=True)

        return result[0].derniere_date if result else None

def sync_user_with_email(doc):
    """
    Gère la création, l'association et la désactivation des utilisateurs
    lors de la modification ou suppression du champ 'email_prescripteur'.
    """
    if not doc.is_new():
        previous_doc = doc.get_doc_before_save()
        previous_email = previous_doc.email_prescripteur
    else:
        previous_email = None

    frappe.logger().info(f"Ancien email : {previous_email}, Nouvel email : {doc.email_prescripteur}")

    if not doc.email_prescripteur:
        # Si l'email est supprimé, désactive l'utilisateur associé à l'ancienne adresse
        if previous_email:
            disable_user_by_email(previous_email)
        doc.utilisateur = None
        return

    # Si l'email a changé, désactive l'utilisateur associé à l'ancienne adresse
    if previous_email and previous_email != doc.email_prescripteur:
        disable_user_by_email(previous_email)

    # Vérifier si un utilisateur existe déjà avec le nouvel email
    existing_user = frappe.db.get_value("User", {"email": doc.email_prescripteur}, "name")

    if existing_user:
        # Associer l'utilisateur existant au prescripteur
        frappe.logger().info(f"Utilisateur existant trouvé : {existing_user}")
        doc.utilisateur = existing_user
        # Activer l'utilisateur s'il est désactivé
        user_doc = frappe.get_doc("User", existing_user)
        if not user_doc.enabled:
            user_doc.enabled = 1
            user_doc.save(ignore_permissions=True)
    else:
        # Créer un nouvel utilisateur
        frappe.logger().info(f"Création d'un nouvel utilisateur pour : {doc.email_prescripteur}")
        user = frappe.get_doc({
            "doctype": "User",
            "first_name": doc.prenom_prescripteur,
            "last_name": doc.nom_prescripteur,
            "email": doc.email_prescripteur,
            "enabled": 1,
            "send_welcome_email": 1,
            "roles": [
                        {"role": "Prescripteur"},
                        {"role": "Raven User"}
                    ]
        })
        user.insert(ignore_permissions=True)
        doc.utilisateur = user.name

def disable_user_by_email(email):
    """
    Désactive un utilisateur basé sur son adresse email.
    """
    user_name = frappe.db.get_value("User", {"email": email}, "name")
    if user_name:
        try:
            frappe.logger().info(f"Tentative de désactivation de l'utilisateur : {user_name} (email : {email})")
            # Désactiver l'utilisateur
            user_doc = frappe.get_doc("User", user_name)
            user_doc.enabled = 0
            user_doc.save(ignore_permissions=True)
            frappe.logger().info(f"Utilisateur désactivé avec succès : {user_name}")
        except Exception as e:
            frappe.log_error(f"Erreur lors de la désactivation de l'utilisateur {user_name}: {str(e)}", "Désactivation Utilisateur")
    else:
        frappe.logger().warning(f"Aucun utilisateur trouvé pour l'email : {email}")

# Hook pour mettre à jour lors d'une modification dans Visite Digitale ou Visite Prescripteur
def update_prescripteur_status_from_visit(doc, method=None):
    """
    Met à jour le statut du prescripteur associé à une visite.
    """
    if not doc.prescripteur:
        return

    prescripteur_doc = frappe.get_doc("Prescripteurs", doc.prescripteur)
    prescripteur_doc.update_status_and_date()
    prescripteur_doc.save(ignore_permissions=True)

# Scheduler pour mettre à jour les statuts des prescripteurs
def update_prescripteurs_status():
    """
    Parcourt tous les prescripteurs et met à jour leurs statuts
    et dates de dernière interaction en fonction des visites.
    """
    # Récupérer tous les prescripteurs
    prescripteurs = frappe.get_all("Prescripteurs", fields=["name"])

    for prescripteur in prescripteurs:
        prescripteur_doc = frappe.get_doc("Prescripteurs", prescripteur.name)
        try:
            prescripteur_doc.update_status_and_date()
            prescripteur_doc.save(ignore_permissions=True)
            frappe.db.commit()  # Commit après chaque mise à jour pour éviter les conflits
        except Exception as e:
            frappe.log_error(f"Erreur lors de la mise à jour du prescripteur {prescripteur.name}: {str(e)}", "Prescripteurs Status Update")

# Ajout automatique d'une ligne dans la Timeline
def log_activity(doc, method):
    """
    Ajoute une ligne dans la section Activité (Timeline) du document Prescripteurs
    avec un design adapté et utilisant le système natif de Frappe.
    """
    if not doc.prescripteur:
        return

    link = frappe.utils.get_url_to_form(doc.doctype, doc.name)
    color_map = {
        "Visite Digitale": "#118ab2",  # Bleu
        "Visite Prescripteur": "#2a9d8f",  # Vert
        "Appel Telephonique": "#ef476f",  # Rouge
    }
    color = color_map.get(doc.doctype, "#000000")  # Par défaut : noir

    if method == "after_insert":
        action = "créée"
    elif method == "on_update":
        action = "mise à jour"
    else:
        action = "modifiée"

    message = (
        f"<b><span style='color:{color};'>{doc.doctype}</span></b> {action} : "
        f"<a href='{link}'><strong>{doc.name}</strong></a>.<br><br>"
    )
    if hasattr(doc, 'notes') and doc.notes:
        notes_box = (
            f"<div class='card border-grey mb-3' style='border: 1px solid #d6d6d6; border-radius: 10px;'>"
            f"  <div class='card-header' style='background-color: #f7f7f7; font-weight: bold;'>⚡ Note</div>"
            f"  <div class='card-body text-dark'>"
            f"    <p>{doc.notes}</p>"
            f"  </div>"
            f"</div>"
        )
        message += notes_box

    prescripteur_doc = frappe.get_doc("Prescripteurs", doc.prescripteur)
    prescripteur_doc.add_comment(
        comment_type="Info",
        text=message
    )

def sync_last_active_with_prescripteur(doc, method):
    """
    Synchronise le champ `last_active` du Doctype `User` avec le champ
    `date_derniere_connexion` du Doctype `Prescripteurs` lorsqu'il est mis à jour.
    """
    if not doc.last_active:
        # Si `last_active` n'est pas défini, aucune action n'est nécessaire
        return

    # Trouve le prescripteur lié à cet utilisateur
    prescripteur = frappe.db.get_value("Prescripteurs", {"utilisateur": doc.name}, "name")

    if prescripteur:
        # Met à jour le champ `date_derniere_connexion` dans le prescripteur
        prescripteur_doc = frappe.get_doc("Prescripteurs", prescripteur)
        prescripteur_doc.date_derniere_connexion = doc.last_active
        prescripteur_doc.save(ignore_permissions=True)
        frappe.logger().info(f"Date de dernière connexion mise à jour pour le prescripteur : {prescripteur}")
