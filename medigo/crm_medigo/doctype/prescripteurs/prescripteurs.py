# -*- coding: utf-8 -*-
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, nowdate, add_days
from frappe.model.document import Document
from frappe import _

class Prescripteurs(Document):
    def before_insert(self):
        # Lors de la création du prescripteur, le statut est défini à 'Nouveau'
        self.status = 'Nouveau'

    def on_update(self):
        # Mettre à jour le statut du prescripteur
        self.update_prescripteur_status()

    def update_prescripteur_status(self):
        """
        Met à jour le champ `status` du prescripteur en fonction des conditions spécifiées.
        """
        # Utiliser un indicateur pour éviter la récursion
        if hasattr(self, '_status_updated') and self._status_updated:
            return
        self._status_updated = True

        prescripteur_name = self.name

        # Calculer la date limite à 90 jours en arrière
        date_limite_90_jours = getdate(add_days(nowdate(), -90))

        # Vérifier s'il existe des visites liées à ce prescripteur
        visites_existantes = frappe.db.sql("""
            SELECT
                MAX(date) AS derniere_date,
                COUNT(*) AS total_visites
            FROM (
                SELECT date FROM `tabVisite Prescripteur` WHERE prescripteur = %s
                UNION ALL
                SELECT date FROM `tabVisite Digitale` WHERE prescripteur = %s
            ) AS visites
        """, (prescripteur_name, prescripteur_name), as_dict=True)[0]

        total_visites = visites_existantes.total_visites or 0
        derniere_date_visite = visites_existantes.derniere_date

        if total_visites == 0:
            # Aucune visite liée : statut 'Non engagé'
            self.status = 'Non engagé'
            frappe.msgprint(f"Le statut du prescripteur {self.name} a été mis à jour à 'Non engagé'.")
            self.date_derniere_interaction = None  # Réinitialiser la date_derniere_interaction
        else:
            if derniere_date_visite:
                date_interaction = getdate(derniere_date_visite)
                self.date_derniere_interaction = date_interaction  # Mettre à jour la date_derniere_interaction

                if date_interaction >= date_limite_90_jours:
                    # Dernière interaction dans les 90 jours : statut 'Engagé'
                    self.status = 'Engagé'
                    frappe.msgprint(f"Le statut du prescripteur {self.name} a été mis à jour à 'Engagé'.")
                else:
                    # Dernière interaction il y a plus de 90 jours : statut 'Inactif'
                    self.status = 'Inactif'
                    frappe.msgprint(f"Le statut du prescripteur {self.name} a été mis à jour à 'Inactif'.")
            else:
                # Ce cas ne devrait pas se produire, mais par précaution :
                self.status = 'Inactif'
                frappe.msgprint(f"Le statut du prescripteur {self.name} a été mis à jour à 'Inactif' (pas de date d'interaction).")
                self.date_derniere_interaction = None

@frappe.whitelist()
def get_heatmap_data(prescripteur):
    """
    Récupère les données pour la heatmap.
    """
    data = {}

    # Compter les visites physiques
    visites_prescripteur = frappe.db.sql("""
        SELECT DATE(creation) AS date, COUNT(*) AS count
        FROM `tabVisite Prescripteur`
        WHERE prescripteur = %s
        GROUP BY DATE(creation)
    """, (prescripteur,), as_dict=True)

    for row in visites_prescripteur:
        data[row.date] = row.count

    # Compter les visites digitales
    visites_digitale = frappe.db.sql("""
        SELECT DATE(creation) AS date, COUNT(*) AS count
        FROM `tabVisite Digitale`
        WHERE prescripteur = %s
        GROUP BY DATE(creation)
    """, (prescripteur,), as_dict=True)

    for row in visites_digitale:
        if row.date in data:
            data[row.date] += row.count
        else:
            data[row.date] = row.count

    return data

def onload(doc, method):
    """
    Ajoute les données au tableau de bord, y compris la heatmap.
    """
    doc.set_onload("dashboard_info", {
        "heatmap": get_heatmap_data(doc.name)
    })

def update_date_derniere_interaction(doc, method=None):
    """
    Met à jour le champ `date_derniere_interaction` pour un prescripteur
    en fonction des interactions les plus récentes dans `Visite Digitale`
    et `Visite Prescripteur`, puis met à jour le statut du prescripteur.
    """
    prescripteur_name = doc.prescripteur  # Nom du prescripteur

    # Charger le document Prescripteurs
    prescripteur_doc = frappe.get_doc("Prescripteurs", prescripteur_name)

    # Appeler la mise à jour du statut
    prescripteur_doc.update_prescripteur_status()

    # Sauvegarder le document sans déclencher on_update pour éviter la récursion
    prescripteur_doc.flags.ignore_on_update = True
    prescripteur_doc.save(ignore_permissions=True)
