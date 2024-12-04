# Copyright (c) 2024, Amine Melizi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate


class VisiteDigitale(Document):
    pass


# Constantes pour les options de canal de communication
CANAL_VALIDE = ["Mixte", "Digital"]


def create_visite_digitale_if_due():
    # Récupérer les prescripteurs avec le canal de communication valide
    prescripteurs = frappe.get_all(
        "Prescripteurs",
        filters={
            "canal": ["in", CANAL_VALIDE]  # Filtrer uniquement sur le canal valide
        },
        fields=["name", "nom_complet_prescripteur", "email_prescripteur"]
    )

    for prescripteur in prescripteurs:
        try:
            # Récupérer la dernière visite digitale pour ce prescripteur
            last_visite_date = frappe.db.get_value(
                "Visite Digitale",
                {"prescripteur": prescripteur.name},
                "creation",
                order_by="creation desc"
            )

            # Vérifier si 90 jours se sont écoulés depuis la dernière visite
            if not last_visite_date or add_days(last_visite_date, 90) <= nowdate():
                # Créer un nouveau document Visite Digitale
                visite = frappe.get_doc({
                    "doctype": "Visite Digitale",
                    "prescripteur": prescripteur.name,
                    "status": "Nouveau"
                })
                visite.insert()

                # Ajouter un log pour la visite créée
                frappe.logger().info(f"Visite Digitale créée pour {prescripteur['name']}")

                # Vérifier si l'email est défini avant d'envoyer une notification
                if prescripteur.email_prescripteur:
                    frappe.sendmail(
                        recipients=prescripteur.email_prescripteur,
                        subject="Nouvelle Visite Digitale",
                        message=f"""
                        Bonjour {prescripteur.nom_complet_prescripteur},
                        
                        Une nouvelle visite digitale a été générée pour vous. Veuillez la compléter dès que possible.
                        """
                    )
                    frappe.logger().info(f"Notification envoyée à {prescripteur['email_prescripteur']}")
                else:
                    frappe.logger().warning(f"Aucun email défini pour {prescripteur['name']}")
        except Exception as e:
            frappe.logger().error(f"Erreur lors de la création de la visite pour {prescripteur['name']}: {str(e)}")
