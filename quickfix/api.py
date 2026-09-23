import frappe

@frappe.whitelist()
def rename_technician(old_name, new_name):
    return frappe.rename_doc(
        "Technician",
        old_name,
        new_name,
        merge=False
    )

@frappe.whitelist()
def transfer_job(from_tech, to_tech):
    try:
        frappe.db.sql("""
            UPDATE `tabJob Card`
            SET assigned_technician = %s
            WHERE assigned_technician = %s
            AND status IN ('Pending Diagnosis', 'In Repair')
        """, (to_tech, from_tech))
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        frappe.log_error(
            frappe.get_traceback(),
            "QuickFix Technician Transfer Error"
        )
        raise
    
def send_jobready_email(job_card_name):
    doc = frappe.get_doc("Job Card", job_card_name)
    frappe.sendmail(
        recipients=[doc.customer_email],
        subject=f"Job Card {doc.name} - Ready for Delivery",
        message=f"""
            Hi {doc.customer_name},<br>
            Your Job Card <b>{doc.name}</b> is ready for delivery.<br>
            Total Amount: ${doc.final_amount}<br>
            Thank you,<br>
            QuickFix
        """
    )    