# Copyright (c) 2024, Amine Melizi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class AppelTelephonique(Document):
    def before_save(self):
        # Génère le contenu HTML et l'assigne au champ HTML du document
        self.html = generer_html_appel(self)

        # Vérifie si le statut a été changé à une des options spécifiées
        rappel_statuses = [
            "À Rappeler - Urgent",
            "À Rappeler - Relance standard",
            "À Rappeler - En attente d'informations"
        ]

        if self.status in rappel_statuses and self.date_rappel:
            # Crée un nouveau document Appel Téléphonique pour rappel
            self.creer_appel_telephonique_rappel()

    def creer_appel_telephonique_rappel(self):
        # Génération du nouveau document pour rappel
        nouveau_appel = frappe.new_doc("Appel Telephonique")
        
        # Copie des informations pertinentes du prescripteur
        nouveau_appel.prescripteur = self.prescripteur
        nouveau_appel.nom_prescripteur = self.nom_prescripteur
        nouveau_appel.titre_prescripteur = self.titre_prescripteur
        nouveau_appel.utilisateur = self.utilisateur
        nouveau_appel.nom_utilisateur = self.nom_utilisateur
        nouveau_appel.type = self.type
        
        # Définit la date et l'heure de rappel
        rappel_date = self.date_rappel
        if rappel_date:
            # Date de rappel assignée
            nouveau_appel.date = rappel_date

            # Définir l'heure de rappel à 9 heures du matin le jour spécifié
            rappel_datetime = datetime.combine(rappel_date, datetime.min.time()).replace(hour=9)
            nouveau_appel.heure = rappel_datetime

        # Statut initialisé à "Nouveau" pour le nouvel appel
        nouveau_appel.status = "Nouveau"

        # Sauvegarde du nouveau document Appel Téléphonique
        nouveau_appel.insert(ignore_permissions=True)
        frappe.msgprint(f"Un nouveau document Appel Téléphonique a été créé pour le rappel le {rappel_date}.")

def generer_html_appel(doc, method=None):
    """
    Génère le contenu des questions en format HTML
    en fonction du type d'appel et des informations du prescripteur.
    """
    frappe.logger().info(f"Génération du contenu HTML pour Appel Téléphonique: {doc.name}")

    # Vérifie si un type d'appel est défini
    if not doc.type:
        frappe.logger().info(f"Aucun type d'appel défini pour le document: {doc.name}")
        return "<p>Aucun type d'appel défini.</p>"

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
        return "<p>Aucun questionnaire correspondant trouvé.</p>"

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

    html_content = f"""
        <div class="appel-telephonique-script">
            <h4>{titre}</h4>
            <p>Bonjour <strong>{prescripteur}</strong>,</p>
            <p>Je suis <strong>{delegue}</strong> de <strong>{default_company}</strong>. 
            Je vous appelle pour vous parler de nos produits et voir si cela pourrait vous intéresser. 
            Est-ce que vous avez un moment pour en discuter ?</p>
            <p>Voici quelques questions que je souhaiterais aborder avec vous :</p>
            <ul>{questions_text}</ul>
            <p>Merci pour votre temps. Je vous enverrai les informations convenues, et nous pourrons, 
            si vous êtes d’accord, programmer un appel de suivi.</p>
        </div>
    """

    return html_content

@frappe.whitelist()
def get_questions_for_html(type, titre_prescripteur=""):
    """
    Méthode pour obtenir les questions du questionnaire correspondant en fonction du type et du titre de prescripteur.
    """
    filters = {"type": type}
    if titre_prescripteur:
        filters["titre_prescripteur"] = titre_prescripteur

    questionnaires = frappe.get_all(
        "Questionnaire Telephonique",
        filters=filters,
        fields=["name"],
        order_by="est_defaut desc, date_creation desc",
        limit=1
    )

    if not questionnaires:
        return []

    questionnaire = frappe.get_doc("Questionnaire Telephonique", questionnaires[0].name)
    return [question.question for question in questionnaire.questions] if questionnaire.questions else []
