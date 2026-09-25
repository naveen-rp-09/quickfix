import frappe
from frappe.query_builder import DocType
from frappe.utils import add_days, now_datetime

@frappe.whitelist()
def rename_technician(old_name, new_name):
    return frappe.rename_doc("Technician",old_name,new_name,)

@frappe.whitelist()
def transfer_job(from_tech, to_tech):
        frappe.db.sql("""UPDATE `tabJob Card` SET technician = %s WHERE technician = %s AND status IN ('Pending Diagnosis', 'In Repair') """, (to_tech, from_tech))
        frappe.db.commit()

def send_email(job_card_name):
    doc = frappe.get_doc("Job Card", job_card_name)
    frappe.sendmail(
        recipients=[doc.customer_email],
        subject=f"Job Card {doc.name} - Ready for Delivery",
        message=f"""{doc.customer_name},Your Job Card <b>{doc.name}</b> is ready for delivery.Total Amount: ${doc.final_amount}"""
    )    

@frappe.whitelist()
def get_job_summary():
    job_card_name = frappe.form_dict.get("job_card_name")

    if not job_card_name or not frappe.db.exists("Job Card", job_card_name):
        return {"error": "404 Not found"}

    doc = frappe.get_doc("Job Card", job_card_name)

    return {
        "name": doc.name,
        "customer_name": doc.customer_name,
        "device_type": doc.device_type,
        "status": doc.status,
        "parts_total": doc.parts_total,
        "labour_charge": doc.labour_charge,
        "final_amount": doc.final_amount
    }   

def get_overdue_jobs():
    JC = DocType("Job Card")
    seven_days = add_days(now_datetime(), -7)
    result = (
        frappe.qb.from_(JC)
        .select(
            JC.name,
            JC.customer_name,
            JC.assigned_technician,
            JC.creation
        ).where((JC.status.isin(["Pending Diagnosis", "In Repair"])) & (JC.creation < seven_days))
        .orderby(JC.creation)
        .run(as_dict=True)
    )
    return result    