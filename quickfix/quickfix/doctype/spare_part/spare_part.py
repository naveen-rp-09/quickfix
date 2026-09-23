# Copyright (c) 2026, quickfix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SparePart(Document):
    def autoname(self):
        self.part_code = self.part_code.upper()
        self.name = frappe.model.naming.make_autoname("PART-.YYYY.-.###")
    
    def validate(self):
        if self.selling_price < self.unit_cost:
            frappe.throw("Selling price cant be lesser than unit cost") 
              
