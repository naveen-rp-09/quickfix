import frappe

# @frappe.whitelist()
def log_change(doc,method=None):
    if(doc.doctype == "Audit Log"):
       return;
    audit = frappe.get_doc({
        "doctype":"Audit Log",
        "doctype_name":doc.doctype,
        "document_name":doc.name,
        "action":method,
        "user":frappe.session.user,
        "timestamp":frappe.utils.now_datetime()
        })
    audit.insert()