import frappe
def get_shop_name():
    return frappe.db.get_single_value("QuickFix Settings","shop_name")