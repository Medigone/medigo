// Copyright (c) 2024, Amine Melizi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Appel Telephonique', {
    refresh: function(frm) {
        if (!frm.is_new() && !frm.doc.notes) {
            generer_notes_script(frm);
        }
    },
    type: function(frm) {
        if (!frm.doc.notes) {
            generer_notes_script(frm);
        }
    },
    titre_prescripteur: function(frm) {
        if (!frm.doc.notes) {
            generer_notes_script(frm);
        }
    }
});

function generer_notes_script(frm) {
    if (!frm.doc.type) {
        frm.set_value('notes', 'Aucun type d\'appel défini.');
        return;
    }

    let titre = frm.doc.type.toUpperCase();
    let default_company = frappe.boot.sysdefaults.company || 'IntraPro Medigo';
    let prescripteur = frm.doc.nom_prescripteur || '[Nom du prescripteur]';
    let delegue = frm.doc.nom_utilisateur || '[Nom du délégué]';

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Questionnaire Telephonique",
            filters: {
                type: frm.doc.type,
                titre_prescripteur: frm.doc.titre_prescripteur || undefined
            },
            fields: ["name"],
            order_by: "est_defaut desc, date_creation desc",
            limit: 1
        },
        callback: function(response) {
            if (response.message && response.message.length > 0) {
                let questionnaire_name = response.message[0].name;

                frappe.call({
                    method: "frappe.client.get",
                    args: {
                        doctype: "Questionnaire Telephonique",
                        name: questionnaire_name
                    },
                    callback: function(res) {
                        if (res.message) {
                            let questions = res.message.questions || [];
                            let questions_text = questions.map((q, index) => `${index + 1}. ${q.question}`).join("\n");

                            let notes_text = `**${titre}**\n
Bonjour **${prescripteur}**,\n
Je suis **${delegue}** de **${default_company}**. Je vous appelle pour vous parler de nos produits et voir si cela pourrait vous intéresser. Est-ce que vous avez un moment pour en discuter ?\n
Voici quelques questions que je souhaiterais aborder avec vous :\n
${questions_text}\n
Merci pour votre temps. Je vous enverrai les informations convenues et nous pourrons, si vous êtes d’accord, programmer un appel de suivi.`;

                            frm.set_value('notes', notes_text);
                        }
                    }
                });
            } else {
                frm.set_value('notes', 'Aucun questionnaire correspondant trouvé.');
            }
        }
    });
}
