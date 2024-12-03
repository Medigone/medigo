frappe.ui.form.on('Appel Telephonique', {
    refresh(frm) {
        // Générer le contenu HTML quand le formulaire est chargé ou rafraîchi
        generer_html_script(frm);
    },
    type(frm) {
        // Re-générer le HTML quand le type est modifié
        generer_html_script(frm);
    },
    titre_prescripteur(frm) {
        // Re-générer le HTML quand le titre du prescripteur est modifié
        generer_html_script(frm);
    }
});

function generer_html_script(frm) {
    // Vérifier si le type d'appel est défini
    if (!frm.doc.type) {
        $(frm.fields_dict['html'].wrapper).html('<p>Aucun type d\'appel défini.</p>');
        return;
    }

    // Requête pour obtenir le questionnaire téléphonique correspondant
    frappe.call({
        method: "medigo.crm_medigo.doctype.appel_telephonique.appel_telephonique.get_questions_for_html",
        args: {
            type: frm.doc.type,
            titre_prescripteur: frm.doc.titre_prescripteur || ""
        },
        callback: function(response) {
            if (response.message) {
                let questions_html = response.message.map((q, index) => `<li>${index + 1}. ${q}</li>`).join("");

                let titre = frm.doc.type.toUpperCase();
                let default_company = frappe.boot.sysdefaults.company || 'IntraPro Medigo';
                let prescripteur = frm.doc.nom_prescripteur || '[Nom du prescripteur]';
                let delegue = frm.doc.nom_utilisateur || '[Nom du délégué]';

                let script_html = `
                    <div class="appel-telephonique-script">
                        <p>Bonjour <strong>${prescripteur}</strong>,</p>
                        <p>Je suis <strong>${delegue}</strong> de <strong>${default_company}</strong>. </br>
                        Je vous appelle pour vous parler de nos produits et voir si cela pourrait vous intéresser. Est-ce que vous avez un moment pour en discuter ?</p>
                        <p>Voici quelques questions que je souhaiterais aborder avec vous :</p>
                        <ul>${questions_html}</ul>
                        <p>Merci pour votre temps. </br>Je vous enverrai les informations convenues, et nous pourrons, si vous êtes d’accord, programmer un appel de suivi.</p>
                    </div>
                `;

                // Injecter le contenu HTML dans le wrapper du champ 'html'
                $(frm.fields_dict['html'].wrapper).html(script_html);
            } else {
                $(frm.fields_dict['html'].wrapper).html('<p>Aucun questionnaire correspondant trouvé.</p>');
            }
        }
    });
}