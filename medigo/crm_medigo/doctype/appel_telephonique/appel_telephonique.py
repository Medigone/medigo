# Copyright (c) 2024, Amine Melizi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AppelTelephonique(Document):
    def before_save(self):
        # Générer des notes seulement si le champ est vide
        if not self.notes:
            generer_notes_appel(self)

def generer_notes_appel(doc, method=None):
    """
    Génère le contenu des questions pour le champ 'notes' en format HTML
    en fonction du type d'appel et des informations du prescripteur.
    """
    frappe.logger().info(f"Génération des notes pour Appel Téléphonique: {doc.name}")

    # Vérifie si un type d'appel est défini
    if not doc.type:
        frappe.logger().info(f"Aucun type d'appel défini pour le document: {doc.name}")
        doc.notes = "<p>Aucun type d'appel défini.</p>"
        return

    # Recherche du questionnaire téléphonique correspondant
    filters = {
        "type": doc.type
    }

    if doc.titre_prescripteur:
        filters["titre_prescripteur"] = doc.titre_prescripteur

    questionnaires = frappe.get_all(
        "Questionnaire Telephonique",
        filters=filters,
        fields=["name"],
        order_by="est_defaut desc, date_creation desc",
        limit=1
    )

    if not questionnaires:
        frappe.logger().info(f"Aucun questionnaire trouvé pour le document: {doc.name}")
        doc.notes = "<p>Aucun questionnaire correspondant trouvé.</p>"
        return

    questionnaire = frappe.get_doc("Questionnaire Telephonique", questionnaires[0].name)
    questions_text = ''

    if questionnaire.questions:
        questions_text = "".join(
            [f"<li>{index + 1}. {question.question}</li>" for index, question in enumerate(questionnaire.questions)]
        )
    else:
        questions_text = "<p>Aucune question disponible pour ce questionnaire.</p>"

    # Génération du texte des notes en HTML
    titre = doc.type.upper()
    default_company = frappe.defaults.get_defaults().get("company") or "IntraPro Medigo"
    prescripteur = doc.nom_prescripteur or '[Nom du prescripteur]'
    delegue = doc.nom_utilisateur or '[Nom du délégué]'

    notes_html = f"""
        <h3>{titre}</h3></br>
        <p>Bonjour <strong>{prescripteur},</strong></p>
        <p>Je suis <strong>{delegue}</strong> de <strong>{default_company}</strong>. 
        Je vous appelle pour vous parler de nos produits et voir si cela pourrait vous intéresser. 
        Est-ce que vous avez un moment pour en discuter ?</p>
        <p>Voici quelques questions que je souhaiterais aborder avec vous :</p>
        <ul>{questions_text}</ul>
        <p>Merci pour votre temps. </br>Je vous enverrai les informations convenues et nous pourrons, 
        si vous êtes d’accord, programmer un appel de suivi.</p>
    """

    # Affecte les notes générées au champ notes du document
    doc.notes = notes_html
    frappe.logger().info(f"Notes générées pour {doc.name}: {doc.notes}")
