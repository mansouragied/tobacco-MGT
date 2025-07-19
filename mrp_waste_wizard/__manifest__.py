
{
    "name": "MO Waste Management",
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "summary": "Add waste tracking to manufacturing orders",
    "author": "Khotawat Consultancy",
    "depends": ["mrp", "stock"],
    "data": [
    "views/mrp_production_view.xml",
    "views/waste_wizard_view.xml",
    "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
