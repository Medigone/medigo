// Copyright (c) 2024, Amine Melizi and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Appel Telephonique", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Appel Telephonique', {
    // Quand le formulaire est chargé ou quand un type d'appel est sélectionné
    type: function(frm) {
        generer_notes_script(frm);
    },
    titre_prescripteur: function(frm) {
        generer_notes_script(frm);
    },
    refresh: function(frm) {
        generer_notes_script(frm);
    }
});

function generer_notes_script(frm) {
    if (!frm.doc.type) {
        frm.set_value('script', '<p>Aucun type d\'appel défini.</p>');
        return;
    }

    // Construction du HTML basé sur les informations du formulaire
    let titre = frm.doc.type.toUpperCase();
    let default_company = frappe.boot.sysdefaults.company || 'IntraPro Medigo';
    let prescripteur = frm.doc.nom_prescripteur || '[Nom du prescripteur]';
    let delegue = frm.doc.nom_utilisateur || '[Nom du délégué]';

    let script_html = `<h3>${titre}</h3>
        <p><b>Bonjour ${prescripteur},</b></p>
        <p>Je suis <b>${delegue}</b> de <b>${default_company}</b>. Je vous appelle pour vous parler de nos produits et voir si cela pourrait vous intéresser. Est-ce que vous avez un moment pour en discuter ?</p>
        <p>Voici quelques questions que je souhaiterais aborder avec vous :</p>
        <p>${generer_questions_html(frm.doc)}</p>
        <p>Merci pour votre temps. Je vous enverrai les informations convenues et nous pourrons, si vous êtes d’accord, programmer un appel de suivi.</p>`;

    // Affecter le HTML généré au champ 'script'
    frm.set_value('script', script_html);
}

function generer_questions_html(doc) {
    // Pour des questions dynamiques, il faudrait effectuer une requête AJAX côté client pour récupérer les questions liées.
    // Ici, un exemple statique pour illustrer.
    let questions = [
        "Connaissez-vous déjà nos produits ?",
        "Êtes-vous ouvert à recevoir plus d’informations ou une documentation concernant nos produits ?",
        "Est-ce que cela pourrait convenir à votre type de patients ?"
    ];

    return questions.map((q, index) => `${index + 1}. ${q}<br>`).join("");
}

