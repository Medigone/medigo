# Copyright (c) 2023, Amine Melizi and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class Evenements(Document):
    def before_save(self):
        self.calculer_total_depenses()

    def calculer_total_depenses(self):
        """
        Calculer la somme des montants dans la table des dépenses
        et mettre à jour le champ total_depenses.
        """
        total = 0
        if self.depenses:
            for depense in self.depenses:
                total += depense.get("montant", 0)  # Ajoute 0 si montant est None ou inexistant
        self.total_depenses = total
