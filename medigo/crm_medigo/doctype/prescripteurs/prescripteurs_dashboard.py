from frappe import _

def get_data():
    return {
        "fieldname": "prescripteur",  # Champ utilisé pour relier les transactions
        "non_standard_fieldnames": {
            "Visite Prescripteur": "prescripteur",
            "Visite Digitale": "prescripteur",
        },
        "transactions": [
            {
                "label": _("Interactions"),
                "items": ["Visite Prescripteur", "Visite Digitale"],
            },
           
        ],
    }

