# Copyright (c) 2024, Amine Melizi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_datetime
from frappe.model.document import Document


class QuestionnaireTelephonique(Document):
	pass


import frappe
from frappe.utils import now_datetime

def update_questionnaire_date(doc, method):
    """
    Met à jour le champ 'date' du document avec la date et l'heure actuelles.
    """
    doc.date = now_datetime()  # Assigner la date actuelle