# -*- coding: utf-8 -*-
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, nowdate, add_days
from frappe.model.document import Document

class Prescripteurs(Document):
    def on_update(self):
        """
        Méthode appelée lors de la mise à jour du document.
        Met à jour le statut et la date de dernière interaction.
        """
        if getattr(self, '_status_updated', False):
            return
        self._status_updated = True
        self.update_status_and_date()

    def before_insert(self):
        """
        Assigne automatiquement la date de création au champ 'Date Création'.
        """
        if not self.date_creation:
            self.date_creation = self.creation

    def update_status_and_date(self):
        """
        Met à jour le champ `status` et `date_derniere_interaction` du prescripteur.
        """
        # Calcul de la date limite à 90 jours
        date_limite_90_jours = getdate(add_days(nowdate(), -90))

        # Récupération de la dernière interaction
        derniere_date = self.get_last_interaction_date()

        if derniere_date:
            self.date_derniere_interaction = derniere_date
            if derniere_date >= date_limite_90_jours:
                self.status = "Engagé"
            else:
                self.status = "Inactif"
        else:
            self.date_derniere_interaction = None
            if self.status != "Nouveau":
                self.status = "Non engagé"

        # Sauvegarde des changements
        self.save(ignore_permissions=True)

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


# Hook pour mettre à jour lors d'une modification dans Visite Digitale ou Visite Prescripteur
def update_prescripteur_status_from_visit(doc, method=None):
    """
    Met à jour le statut du prescripteur associé à une visite.
    """
    if not doc.prescripteur:
        return

    prescripteur_doc = frappe.get_doc("Prescripteurs", doc.prescripteur)
    prescripteur_doc.update_status_and_date()


# Scheduler pour mettre à jour les statuts des prescripteurs toutes les 2 minutes
def update_prescripteurs_status():
    """
    Parcourt tous les prescripteurs et met à jour leurs statuts
    et dates de dernière interaction en fonction des visites.
    """
    # Récupérer tous les prescripteurs
    prescripteurs = frappe.get_all("Prescripteurs", fields=["name", "status", "date_derniere_interaction"])

    for prescripteur in prescripteurs:
        prescripteur_doc = frappe.get_doc("Prescripteurs", prescripteur.name)
        try:
            prescripteur_doc.update_status_and_date()
            frappe.db.commit()  # Commit après chaque mise à jour pour éviter les conflits
        except Exception as e:
            frappe.log_error(f"Erreur lors de la mise à jour du prescripteur {prescripteur.name}: {str(e)}", "Prescripteurs Status Update")


# Ajout automatique d'une ligne dans la Timeline
def log_activity(doc, method):
    """
    Ajoute une ligne dans la section Activité (Timeline) du document Prescripteurs
    avec un message adapté à l'événement (création ou mise à jour).
    """
    # Vérifiez si le document est lié à un prescripteur
    if not doc.prescripteur:
        return

    # Générer un lien HTML pointant vers le document
    link = frappe.utils.get_url_to_form(doc.doctype, doc.name)

    # Déterminer le code couleur en fonction du type d'activité
    color_map = {
        "Visite Digitale": "#457b9d",  # Bleu doux
        "Visite Prescripteur": "#2a9d8f",  # Rouge
        "Appel Telephonique": "#e63946",  # Vert
    }
    color = color_map.get(doc.doctype, "#000000")  # Par défaut : noir

    # Construire le message
    if method == "after_insert":
        action = "créée"
    elif method == "on_update":
        action = "mise à jour"
    else:
        action = "modifiée"

    message = (
        f"<b><span style='color:{color};'>{doc.doctype}</span></b> {action} : "
        f"<a href='{link}'>{doc.name}</a>."
    )

    # Ajouter des notes si disponibles
    if hasattr(doc, 'notes') and doc.notes:
        # Créer un conteneur unique avec fond gris clair et bordures arrondies
        notes_box = (
            f"<div style='border: 1px solid #d3d3d3; border-radius: 10px; padding: 10px; margin-top: 10px; "
            f"background-color: #f7f7f7; font-size: 14px; color: #333;'>"
            f"<strong style='display: block; margin-bottom: 5px;'>⚡ Notes :</strong>"
            f"<div style='background-color: #ffffff; padding: 10px; border-radius: 5px;'>"
            f"{doc.notes}"
            f"</div>"
            f"</div>"
        )
        message += notes_box

    # Ajouter une entrée dans la Timeline
    frappe.get_doc("Prescripteurs", doc.prescripteur).add_comment(
        comment_type="Info",
        text=message
    )

def before_save(self):
        """
        Convertit automatiquement les champs en majuscules avant la sauvegarde.
        """
        if self.nom_prescripteur:
            self.nom_prescripteur = self.nom_prescripteur.upper()

        if self.prenom_prescripteur:
            self.prenom_prescripteur = self.prenom_prescripteur.upper()

        if self.nom_complet_prescripteur:
            self.nom_complet_prescripteur = self.nom_complet_prescripteur.upper()