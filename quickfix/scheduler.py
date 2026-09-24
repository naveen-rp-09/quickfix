import frappe
from frappe.utils import today

def check_low_stock():
    last_run = frappe.db.get_value(
        "Audit Log",
        {
            "action": "low_stock_check",
            "timestamp": ["between", [
                f"{today()} 00:00:00",
                f"{today()} 23:59:59"
            ]]
        },
        "name" 
    )

    if last_run:
        return

    enabled = frappe.db.get_single_value(
        "QuickFix Settings",
        "low_stock_alert_enabled"
    )

    if not enabled:
        return

    spare_parts = frappe.get_all(
        "Spare Part",
        filters={
            "is_active": 1
        },
        fields=[
            "name",
            "part_name",
            "stock_qty",
            "reorder_level"
        ]
    )

    low_stock_parts = []

    for part in spare_parts:
        if part.stock_qty <= part.reorder_level:
            low_stock_parts.append(part)
            frappe.log_error(
                f"Low stock: {part.part_name} "
                f"(Stock: {part.stock_qty}, "
                f"Reorder Level: {part.reorder_level})",
                "QuickFix Low Stock Alert"
            )
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Spare Part",
        "document_name": "Daily Low Stock Check",
        "action": "low_stock_check",
        "user": frappe.session.user,
        "timestamp": frappe.utils.now_datetime()
    }).insert(
        ignore_permissions=True
    )