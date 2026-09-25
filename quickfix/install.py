import frappe

def after_install():
    create_default_device_types()
    create_default_settings()
    frappe.msgprint("QuickFix installed successfully!")

def create_default_device_types():
    device_types = ["Smartphone","Laptop","Tablet"]
    for device_type in device_types:
        if not frappe.db.exists("Device Type",device_type):
            doc = frappe.get_doc({
                "doctype": "Device Type",
                "device_type": device_type
            })
            doc.insert(ignore_permissions=True)

def create_default_settings():
    if not frappe.db.exists("QuickFix Settings","QuickFix Settings"):
        settings = frappe.get_doc({
            "doctype": "QuickFix Settings",
            "shop_name": "QuickFix Service Centre",
            "manager_email": "manager@quickfix.com",
            "default_labour_charge": 500,
            "low_stock_alert_enabled": 1
        })
        settings.insert(ignore_permissions=True)
        