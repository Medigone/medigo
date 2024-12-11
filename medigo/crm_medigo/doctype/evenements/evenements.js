// Copyright (c) 2023, Amine Melizi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Evenements", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Evenements", "refresh", function(frm) {
    frm.fields_dict['etablissement'].grid.get_field('service').get_query = function(doc, cdt, cdn) {
        var child = locals[cdt][cdn];
        //console.log(child);
        return {    
            filters:[
                ['etablissement', '=', child.etablissement]
            ]
        }
    }
});
 
// frappe.ui.form.on("Depenses Evenement", {
//     montant: function(frm, cdt, cdn) {
//         var d = locals[cdt][cdn];
//         var total = 0;
//         frm.doc.depenses.forEach(function(row) { 
//             total += row.montant || 0; // Ajoute 0 si montant est null ou undefined
//         });
//         frm.set_value("total_depenses", total);
//         refresh_field("total_depenses");
//     },
//     depenses_remove: function(frm, cdt, cdn) {
//         var total = 0;
//         frm.doc.depenses.forEach(function(row) { 
//             total += row.montant || 0; // Ajoute 0 si montant est null ou undefined
//         });
//         frm.set_value("total_depenses", total);
//         refresh_field("total_depenses");
//     }
// });

frappe.ui.form.on("Depenses Evenement", {
    montant: function(frm, cdt, cdn) {
        calculer_total_depenses(frm); // Appel de la fonction pour calculer
    },
    depenses_remove: function(frm, cdt, cdn) {
        calculer_total_depenses(frm); // Appel de la fonction pour calculer après suppression
    }
});

function calculer_total_depenses(frm) {
    var total = 0;
    if (frm.doc.depenses) {
        frm.doc.depenses.forEach(function(row) {
            total += row.montant || 0; // Ajoute 0 si montant est null ou undefined
        });
    }
    frm.set_value("total_depenses", total);
    refresh_field("total_depenses");
}


frappe.ui.form.on('Evenements', {
    refresh: function(frm) {
        mettre_a_jour_barre_progression(frm);
    },
    total_depenses: function(frm) {
        mettre_a_jour_barre_progression(frm);
    },
    budget_prevu: function(frm) {
        mettre_a_jour_barre_progression(frm);
    }
});

function mettre_a_jour_barre_progression(frm) {
    // Calculer la progression
    let progression = 0;
    if (frm.doc.budget_prevu && frm.doc.budget_prevu > 0) {
        progression = (frm.doc.total_depenses / frm.doc.budget_prevu) * 100;
    }

    // Définir la couleur en fonction de la progression
    let couleur = '#2a9d8f'; // Vert
    if (progression > 70 && progression <= 100) {
        couleur = '#f4a261'; // Orange entre 70% et 100%
    } else if (progression > 100) {
        couleur = '#e63946'; // Rouge au-delà de 100%
    }

    // Générer le HTML de la barre de progression
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

    // Injecter le HTML dans le champ progression_bar
    $(frm.fields_dict.progression_bar.wrapper).html(barre_progression);
}
