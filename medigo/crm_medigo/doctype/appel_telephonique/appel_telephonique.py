# Copyright (c) 2024, Amine Melizi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AppelTelephonique(Document):
    pass

def generer_notes_appel(doc, method):
    """
    Génère le script des questions pour le champ 'script' en fonction du type d'appel
    et des informations du prescripteur. Laisse le champ 'notes' pour les réponses.
    """
    frappe.logger().info(f"Génération du script pour Appel Téléphonique: {doc.name}")

    # Vérifie si un type d'appel est défini
    if not doc.type:
        frappe.logger().info(f"Aucun type d'appel défini pour le document: {doc.name}")
        return  # Si aucun type d'appel n'est défini, on ne génère pas de script

    # Recherche du questionnaire téléphonique
    filters = {
        "type": doc.type
    }

    if doc.titre_prescripteur:
        filters["titre_prescripteur"] = doc.titre_prescripteur

    # Recherche le questionnaire correspondant sans inclure le champ 'questions'
    questionnaires = frappe.get_all("Questionnaire Telephonique", filters=filters, fields=["name"], order_by="est_defaut desc, date desc", limit=1)

    if questionnaires:
        frappe.logger().info(f"Questionnaire trouvé pour le document {doc.name}: {questionnaires[0].name}")
        questionnaire = frappe.get_doc("Questionnaire Telephonique", questionnaires[0].name)
        questions_text = ''

        # Concatène les questions dans une chaîne de caractères
        if questionnaire.questions:
            for index, question in enumerate(questionnaire.questions):
                questions_text += f"{index + 1}. {question.question}<br>"
        else:
            questions_text = 'Aucune question disponible pour ce questionnaire.'

        # Récupère la société par défaut
        default_company = frappe.defaults.get_defaults().get("company") or "IntraPro Medigo"

        # Générez le script HTML pour les questions
        titre = doc.type.upper()
        script_html = f"<h3>{titre}</h3>" \
                      f"<p><b>Bonjour {doc.nom_prescripteur or '[Nom du prescripteur]'},</b></p>" \
                      f"<p>Je suis <b>{doc.nom_utilisateur or '[Nom du délégué]'}</b> de <b>{default_company}</b>. " \
                      f"Je vous appelle pour vous parler de nos produits et voir si cela pourrait vous intéresser. Est-ce que vous avez un moment pour en discuter ?</p>" \
                      f"<p>Voici quelques questions que je souhaiterais aborder avec vous :</p>" \
                      f"<p>{questions_text}</p>" \
                      f"<p>Merci pour votre temps. Je vous enverrai les informations convenues et nous pourrons, si vous êtes d’accord, programmer un appel de suivi.</p>"

        # Affecte le script HTML généré au champ 'script' du document
        doc.script = script_html
        frappe.logger().info(f"Script HTML généré pour le document {doc.name}: {doc.script}")
    else:
        frappe.logger().info(f"Aucun questionnaire trouvé pour le document: {doc.name}")
        doc.script = "<p>Aucun questionnaire correspondant n'a été trouvé.</p>"

    # Sauvegarde le document si nécessaire
    if method == "after_insert":
        doc.save()
