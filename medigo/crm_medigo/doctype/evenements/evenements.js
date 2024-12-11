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


frappe.ui.form.on("Evenements", {
    total_depenses: function(frm) {
        mettre_a_jour_progression(frm);
    },
    budget_prevu: function(frm) {
        mettre_a_jour_progression(frm);
    }
});

function mettre_a_jour_progression(frm) {
    if (frm.doc.budget_prevu && frm.doc.budget_prevu > 0) {
        let progression = (frm.doc.total_depenses / frm.doc.budget_prevu) * 100;
        progression = Math.min(progression, 100); // Limite à 100% pour éviter des dépassements visuels
        frm.set_value("progression_depenses", progression);
    } else {
        frm.set_value("progression_depenses", 0); // Si budget_prevu est 0 ou non défini
    }
}
