# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class JobCard(Document):
      
 def autoname(self):
   self.name = frappe.model.naming.make_autoname("JC-.YYYY.-.#####")
   
#  def get_permission_query_conditions(user):
#     if not user:
#         user = frappe.session.user
#     if "QF Manager" in frappe.get_roles(user):
#         return ""
#     if "QF Technician" in frappe.get_roles(user):
#         technician = frappe.db.get_value(
#             "Technician",
#             {"user": user},
#             "name"
#         )
#         if technician:
#           return f"`tabJob Card`.assigned_technician = {frappe.db.escape(technician)}"
#         return "1=0"
#     return "" 
     
 def validate(self):
         phone = self.customer_phone
         if len(phone)!=10:
             frappe.throw("Phone Number Cant be less than 10 digits")
         
         repair_statuses = [
             "In Repair",
             "ReadyforDelivery",
             "Delivered"
		 ]
         
         if self.status in repair_statuses and not self.technician :
             frappe.throw("Assigned Technician is required when staus is" f"'{self.status}'.")
         
         parts_total = 0
         
         for row in self.parts_used or []:
            row.total_price = (row.quantity or 0)*(row.unit_price or 0)
            parts_total+=flt(row.total_price)
         
         self.parts_total = parts_total
         
         if not self.labour_charge:
             
             labour_charge = frappe.db.get_single_value(
				 "QuickFix Settings",
                  "default_labour_charge"
			 )
             self.labour_charge = labour_charge
         
         self.final_amount = self.parts_total + self.labour_charge     
 #before-on           
 def before_submit(self):
    
    if self.status!="ReadyforDelivery":
        frappe.throw("This records cant be submitted until its status is Ready for Delivery.")         
    
    for row in self.parts_used or []:
        stock_qty = frappe.db.get_value(
            "Spare Part",
            row.part,
            "stock_qty",
            ) or 0
        if stock_qty <= row.quantity:
            part_name = frappe.db.get_value(
				"Spare Part",
				row.part,
				"stock_qty",
			) or row.part
            frappe.throw(f"Insufficient stock for {part_name} requiered {row.quanity} but available {stock_qty} ")            
#on-after             
 def on_submit(self):
    
    for row in self.parts_used or []:
        current_qty = frappe.db.get_value(
            "Spare Part",
            row.part,
            "stock_qty",
            ) or 0
        frappe.db.set_value(
			"Spare Part",
			 row.part,
			"stock_qty",
            current_qty-row.quantity,
            update_modified= False 
		)
        
        existing_invoice = frappe.db.exists("Service Invoice",{"job_card": self.name})
        if not existing_invoice:
        
            invoice = frappe.get_doc({
	            "doctype":"Service Invoice",
                "job_card":self.name,
                "labour_charge":self.labour_charge,
                "parts_total":self.parts_total,
                "total_amount":self.final_amount,
                "payment_status":self.payment_status
	        })
    
            invoice.insert(ignore_permissions=True)
    
    frappe.enqueue(
		"quicfix.quicfix.api.send_jobready_email",
         job_card_name = self.name,
         queue="short"
	)

 def on_cancel(self):
    
        for row in self.parts_used or []:
            current_qty = frappe.db.get_value(
				"Spare Part",
				row.part,
				"stock_qty",
				) or 0
            frappe.db.set_value(
					"Spare Part",
					row.part,
					"stock_qty",
					current_qty+row.quantity,
					update_modified= False 
				)
        
        invoice_name = frappe.db.get_value(
			"Service Invoice",
             {
				"job_card": self.name 
			 },
             "name"
		)
        if invoice_name :
            invoice = frappe.get_doc(
				"Service Invoice",
                 invoice_name
			)
            if invoice.docstatus==1:
                invoice.cancel()
                
 def on_trash(self):
    allowed_statuses = ["cancelled","Draft"]
    if self.status not in allowed_statuses:
        frappe.throw("The document cant be deleted untill its status is draft or cancelled") 
 
#  def on_update(self):
#      self.save()              
         
 @frappe.whitelist()    
 def unsafe_jobcard():
        return frappe.get_all(
            "Job Card",
            fields=["*"]
            ); 
        
 @frappe.whitelist()
 def safe_jobcard():
    fields=[
        "name",
        "customer_name",
        "customer_phone",
        "customer_email",
        "device_type",
        "device_brand",
        "device_model",
        "imei_or_serial",
        "status",
        "creation"
	]
    
    jobs=frappe.get_list("Job Card",fields=fields)
    
    if "QF Manager" not in frappe.get_roles():
        for job in jobs:
            job.pop("customer_phone",None)
            job.pop("customer_email",None)        
    
    return jobs   
 
def before_print(doc, method=None, print_settings=None):
    doc.print_summary = (
        f"{doc.customer_name} - "f"{doc.device_type}"
    )
    