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
 
frappe.ui.form.on("Depenses Evenement", {
    montant: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total = 0;
        frm.doc.depenses.forEach(function(row) { 
            total += row.montant || 0; // Ajoute 0 si montant est null ou undefined
        });
        frm.set_value("total_depenses", total);
        refresh_field("total_depenses");
    },
    depenses_remove: function(frm, cdt, cdn) {
        var total = 0;
        frm.doc.depenses.forEach(function(row) { 
            total += row.montant || 0; // Ajoute 0 si montant est null ou undefined
        });
        frm.set_value("total_depenses", total);
        refresh_field("total_depenses");
    }
});

