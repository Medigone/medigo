# Copyright (c) 2023, Amine Melizi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Evenements(Document):
    def before_save(self):
        # Calculer le total des dépenses
        self.calculer_total_depenses()
        # Calculer l'écart budgétaire
        self.calculer_ecart_budget()
        # Calculer le taux de participation
        self.calculer_taux_participation()

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

    def calculer_ecart_budget(self):
        """
        Calculer l'écart budgétaire en fonction du budget prévu
        et des dépenses totales.
        """
        if self.budget_prevu is not None and self.total_depenses is not None:
            self.ecart_budget = self.budget_prevu - self.total_depenses
        else:
            self.ecart_budget = 0  # Par défaut, 0 si les champs sont vides

    def calculer_taux_participation(self):
        """
        Calculer le taux de participation basé sur le nombre de participants présents
        et le nombre d'invités.
        """
        if self.participants_invites and self.participants_invites > 0:
            self.taux_participation = (self.participants_presents / self.participants_invites) * 100
        else:
            self.taux_participation = 0  # Par défaut, 0 si les données sont insuffisantes
