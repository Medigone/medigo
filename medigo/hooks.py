app_name = "medigo"
app_title = "Medigo"
app_publisher = "Amine Melizi"
app_description = "CRM Medical"
app_email = "admin@medigo.one"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/medigo/css/styles.css"
# app_include_js = "/assets/medigo/js/medigo.js"

# include js, css files in header of web template
# web_include_css = "/assets/medigo/css/medigo.css"
# web_include_js = "/assets/medigo/js/medigo.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "medigo/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "medigo/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

role_home_page = {
    "Prescripteur": "accueil-prescripteurs",
    "Raven User": "accueil-prescripteurs"
}

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "medigo.utils.jinja_methods",
#	"filters": "medigo.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "medigo.install.before_install"
# after_install = "medigo.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "medigo.uninstall.before_uninstall"
# after_uninstall = "medigo.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "medigo.utils.before_app_install"
# after_app_install = "medigo.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "medigo.utils.before_app_uninstall"
# after_app_uninstall = "medigo.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "medigo.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# hooks.py

# hooks.py

doc_events = {
    "Appel Telephonique": {
        "before_save": [
            "medigo.crm_medigo.doctype.appel_telephonique.appel_telephonique.generer_html_appel"
        ]
    },
    "Visite Digitale": {
        "after_insert": [
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.log_activity",
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.update_prescripteur_status_from_visit"
        ],
        "on_update": [
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.update_prescripteur_status_from_visit"
        ],
        "on_trash": [
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.update_prescripteur_status_from_visit"
        ]
    },
    "Visite Prescripteur": {
        "after_insert": [
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.log_activity",
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.update_prescripteur_status_from_visit"
        ],
        "on_update": [
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.update_prescripteur_status_from_visit"
        ],
        "on_trash": [
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.update_prescripteur_status_from_visit"
        ]
    },
    "Questionnaire Telephonique": {
        "before_save": [
            "medigo.crm_medigo.doctype.questionnaire_telephonique.questionnaire_telephonique.update_questionnaire_date"
        ]
    },
    "User": {
        "on_update": "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.sync_last_active_with_prescripteur"
    }
}



# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------
scheduler_events = {
    "cron": {
        # Exécute à 3h du matin tous les 3 jours
        "0 3 */3 * *": [
            "medigo.crm_medigo.doctype.prescripteurs.prescripteurs.update_prescripteurs_status"
        ],
        # Exécute à 4h du matin tous les 3 mois
        "0 4 1 */3 *": [
            "medigo.crm_medigo.doctype.visite_digitale.visite_digitale.create_visite_digitale_if_due"
        ]
    }
}



# scheduler_events = {
#	"all": [
#		"medigo.tasks.all"
#	],
#	"daily": [
#		"medigo.tasks.daily"
#	],
#	"hourly": [
#		"medigo.tasks.hourly"
#	],
#	"weekly": [
#		"medigo.tasks.weekly"
#	],
#	"monthly": [
#		"medigo.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "medigo.install.before_tests"

# Overriding Methods
# ------------------------------
#

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "medigo.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["medigo.utils.before_request"]
# after_request = ["medigo.utils.after_request"]

# Job Events
# ----------
# before_job = ["medigo.utils.before_job"]
# after_job = ["medigo.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"medigo.auth.validate"
# ]
fixtures = [
    "Communes",
    "Objectif Visite",
    "Titre Prescripteur",
    "Type Etablissement",
    "Type Service",
    "Wilayas",
    "Zone",
    "Contrepartie",
    "Role",
    "Role Profile",
    "Raisons absence",
    "Lieux evenements",
    "Type Action",
    "Custom DocPerm",
    "Server Script",
    "Client Script",
]