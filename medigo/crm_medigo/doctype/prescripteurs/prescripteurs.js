// Copyright (c) 2023, Amine Melizi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Prescripteurs", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Prescripteurs", {
	onload: function(frm) {
		frm.set_query("service", function() {
			return {
				filters: [
					["etablissement", "in", [frm.doc.etablissement]]
				]
			};
		});
	}
});


frappe.ui.form.on('Prescripteurs', {
    nom_prescripteur: function(frm) {
        updateNomCompletPrescripteur(frm);
    },

    prenom_prescripteur: function(frm) {
        updateNomCompletPrescripteur(frm);
    }
});

function updateNomCompletPrescripteur(frm) {
    let nom_prescripteur = frm.doc.nom_prescripteur;
    let prenom_prescripteur = frm.doc.prenom_prescripteur;

    if (nom_prescripteur && prenom_prescripteur) {
        let nom_complet_prescripteur = nom_prescripteur + " " + prenom_prescripteur;
        frm.set_value('nom_complet_prescripteur', nom_complet_prescripteur);
    }
}

frappe.ui.form.on('Prescripteurs', {
    onload: function(frm) {
        // Vérifiez que les données sont disponibles
        if (frm.doc.__onload && frm.doc.__onload.dashboard_info) {
            const heatmap_data = frm.doc.__onload.dashboard_info.heatmap;

            if (heatmap_data) {
                // Ajouter un conteneur pour la heatmap si nécessaire
                if (!$("#heatmap").length) {
                    frm.dashboard.add_section('<div id="heatmap" style="height: 200px;"></div>');
                }

                // Afficher la heatmap
                frappe.dashboard_utils.render_heatmap({
                    parent: $("#heatmap")[0],
                    data: heatmap_data,
                    date_field: "creation",
                    heatmap_message: __("Aucune activité trouvée"),
                    base_date: frappe.datetime.now_date()
                });
            }
        }
    }
});
