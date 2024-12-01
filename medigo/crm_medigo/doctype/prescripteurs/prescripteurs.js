// Copyright (c) 2023, Amine Melizi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Prescripteurs", {
    onload: function(frm) {
        // Définir la requête dynamique pour le champ "service"
        frm.set_query("service", function() {
            return {
                filters: [
                    ["etablissement", "in", [frm.doc.etablissement]]
                ]
            };
        });

        // Charger et afficher la heatmap si les données sont disponibles
        if (frm.doc.__onload && frm.doc.__onload.dashboard_info) {
            const heatmap_data = frm.doc.__onload.dashboard_info.heatmap;

            if (heatmap_data) {
                // Ajouter un conteneur pour la heatmap si nécessaire
                if (!$("#heatmap").length) {
                    frm.dashboard.add_section('<div id="heatmap" style="height: 200px;"></div>');
                }

                // Rendre la heatmap
                frappe.dashboard_utils.render_heatmap({
                    parent: $("#heatmap")[0],
                    data: heatmap_data,
                    date_field: "creation",
                    heatmap_message: __("Aucune activité trouvée"),
                    base_date: frappe.datetime.now_date()
                });
            }
        }
    },

    // Convertir automatiquement les champs en majuscules
    nom_prescripteur: function(frm) {
        handleFieldUpdate(frm, "nom_prescripteur");
    },

    prenom_prescripteur: function(frm) {
        handleFieldUpdate(frm, "prenom_prescripteur");
    },

    nom_complet_prescripteur: function(frm) {
        handleFieldUpdate(frm, "nom_complet_prescripteur");
    }
});

// Fonction pour convertir en majuscules et mettre à jour le nom complet
function handleFieldUpdate(frm, fieldname) {
    if (frm.doc[fieldname]) {
        // Convertir le champ en majuscules
        frm.set_value(fieldname, frm.doc[fieldname].toUpperCase());
    }

    // Mettre à jour le champ "nom_complet_prescripteur" si les champs nom/prénom sont modifiés
    if (fieldname === "nom_prescripteur" || fieldname === "prenom_prescripteur") {
        updateNomCompletPrescripteur(frm);
    }
}

// Fonction pour mettre à jour "nom_complet_prescripteur"
function updateNomCompletPrescripteur(frm) {
    const { nom_prescripteur, prenom_prescripteur } = frm.doc;

    if (nom_prescripteur && prenom_prescripteur) {
        const nom_complet = `${nom_prescripteur} ${prenom_prescripteur}`.toUpperCase();
        frm.set_value("nom_complet_prescripteur", nom_complet);
    }
}
