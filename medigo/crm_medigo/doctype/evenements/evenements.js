// Gestion des événements pour le Doctype "Evenements"
frappe.ui.form.on("Evenements", {
    refresh: function(frm) {
        mettre_a_jour_barre_progression(frm);
    },
    budget_prevu: function(frm) {
        calculer_ecart_budget(frm);
        mettre_a_jour_barre_progression(frm);
    },
    total_depenses: function(frm) {
        calculer_ecart_budget(frm);
        mettre_a_jour_barre_progression(frm);
    },
    participants_presents: function(frm) {
        calculer_taux_participation(frm);
    },
    participants_invites: function(frm) {
        calculer_taux_participation(frm);
    }
});

// Gestion des événements pour le Doctype enfant "Depenses Evenement"
frappe.ui.form.on("Depenses Evenement", {
    montant: calculer_total_depenses,
    depenses_remove: calculer_total_depenses
});

// Fonction pour calculer le total des dépenses
function calculer_total_depenses(frm) {
    let total = 0;
    if (frm.doc.depenses) {
        frm.doc.depenses.forEach(row => {
            total += row.montant || 0; // Ajouter 0 si montant est null ou undefined
        });
    }
    frm.set_value("total_depenses", total);
}

// Fonction pour mettre à jour la barre de progression
function mettre_a_jour_barre_progression(frm) {
    let progression = 0;
    if (frm.doc.budget_prevu && frm.doc.budget_prevu > 0) {
        progression = (frm.doc.total_depenses / frm.doc.budget_prevu) * 100;
    }

    let couleur = '#2a9d8f'; // Vert
    if (progression > 70 && progression <= 100) {
        couleur = '#f4a261'; // Orange entre 70% et 100%
    } else if (progression > 100) {
        couleur = '#e63946'; // Rouge au-delà de 100%
    }

    const barre_progression = `
        <div style="width: 100%; margin-top: 0px; margin-bottom: 15px;">
            <label>Progression des Dépenses (${Math.round(progression)}%)</label>
            <div class="progress" style="height: 10px;">
                <div class="progress-bar" role="progressbar" 
                    style="width: ${progression}%; background-color: ${couleur};" 
                    aria-valuenow="${progression}" aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
        </div>
    `;
    $(frm.fields_dict.progression_bar.wrapper).html(barre_progression);
}

// Fonction pour calculer l'écart budgétaire
function calculer_ecart_budget(frm) {
    if (frm.doc.budget_prevu && frm.doc.total_depenses) {
        let ecart = frm.doc.budget_prevu - frm.doc.total_depenses;
        frm.set_value('ecart_budget', ecart);
    } else {
        frm.set_value('ecart_budget', 0);
    }
}

// Fonction pour calculer le taux de participation
function calculer_taux_participation(frm) {
    if (frm.doc.participants_presents !== undefined && frm.doc.participants_invites > 0) {
        let taux = (frm.doc.participants_presents / frm.doc.participants_invites) * 100;
        frm.set_value('taux_participation', taux.toFixed(2)); // Limite à 2 décimales
    } else {
        frm.set_value('taux_participation', 0); // Défaut si les données sont insuffisantes
    }
}
