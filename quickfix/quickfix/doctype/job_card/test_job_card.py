# Copyright (c) 2026, quickfix and Contributors
# See license.txt

# import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]

import frappe
import unittest

class TestJobCard(unittest.TestCase):

    def tearDown(self):
        frappe.set_user("Administrator")

    def test_job_card(self):
        doc = frappe.get_doc({
            "doctype": "Job Card",
            "customer_name": "Test Customer-01",
            "customer_phone": "9876543210"
        })
        doc.insert()
        self.assertEqual(doc.docstatus, 0)

    def test_phone(self):
     doc = frappe.get_doc({
        "doctype": "Job Card",
        "customer_name": "Test Customer-02",
        "customer_phone": "9876543210"
    })
     doc.insert()
     self.assertTrue(doc.name)

    def test_spare_part_price(self):
        part = frappe.get_doc({
            "doctype": "Spare Part",
            "part_code": "TEST100",
            "part_name": "Test Part",
            "unit_cost": 100,
            "selling_price": 100,
            "stock_qty": 10
        })
        part.insert()
        self.assertTrue(part.name)
        
    def test_final_amount(self):

     part = frappe.get_doc({
        "doctype": "Spare Part",
        "part_code": "TEST150",
        "part_name": "Test Part",
        "unit_cost": 100,
        "selling_price": 150,
        "stock_qty": 10
    }).insert()

     doc = frappe.get_doc({
        "doctype": "Job Card",
        "customer_name": "Test Customer-03",
        "customer_phone": "9876543210",
        "labour_charge": 500,
        "parts_used": [{
             "part": part.name,
             "unit_price": 150,
             "quantity": 2
         }]
    })
     
     doc.insert()
     self.assertEqual(doc.parts_total, 300)
     self.assertEqual(doc.final_amount, 800)

    def test_stock(self):
        part = frappe.get_doc({
            "doctype": "Spare Part",
            "part_code": "TEST200",
            "part_name": "Test Part",
            "unit_cost": 100,
            "selling_price": 150,
            "stock_qty": 5
        }).insert()
        tech = frappe.get_doc({
	        "doctype":"Technician",
            "technician_name":"TESTER TECHNICIAN-100"
		}).insert()
        doc = frappe.get_doc({
            "doctype": "Job Card",
            "customer_name": "Test Customer-04",
            "customer_phone": "9876543210",
            "status":"ReadyforDelivery",
            "technician":tech.name,
            "parts_used":[
                 {
                    "part": part.name,
                    "unit_price":150,
                    "quantity": 1
                 }
			]
        })
        doc.insert()
        doc.submit()
        stock = frappe.db.get_value(
            "Spare Part",
            part.name,
            "stock_qty"
        )
        self.assertEqual(stock, 4)

    
    def test_cancel(self):

        part = frappe.get_doc({
            "doctype": "Spare Part",
            "part_code": "TEST250",
            "part_name": "Test Part",
            "unit_cost": 100,
            "selling_price": 150,
            "stock_qty": 5
        }).insert()
        tech = frappe.get_doc({
			"doctype":"Technician",
			"technician_name":"TESTER TECHNICIAN-200"
		}).insert()
        doc = frappe.get_doc({
            "doctype": "Job Card",
            "customer_name": "Testingcancel-100",
            "customer_phone": "9876543210",
            "status":"ReadyforDelivery",
			"technician":tech.name,
			"parts_used":[
							 {
								"part": part.name,
								"unit_price":150,
								"quantity": 1
							 }
						]
        })
        doc.insert()
        doc.submit()
        doc.cancel()
        stock = frappe.db.get_value(
            "Spare Part",
            part.name,
            "stock_qty"
        )
        self.assertEqual(stock, 5)

    def test_duplicate_invoice(self):

        part = frappe.get_doc({
            "doctype": "Spare Part",
            "part_code": "TEST800",
            "part_name": "Test Part",
            "unit_cost": 100,
            "selling_price": 150,
            "stock_qty": 5
        }).insert()
        tech = frappe.get_doc({
			"doctype":"Technician",
			"technician_name":"TESTER TECHNICIAN-300"
			}).insert()
        doc = frappe.get_doc({
            "doctype": "Job Card",
            "customer_name": "Test Customer-007",
            "customer_phone": "9876543210",
            "status":"ReadyforDelivery",
			"technician":tech.name,
			"parts_used":[
				{
				 "part": part.name,
				 "unit_price":150,
				 "quantity": 1
				}
			]
        })
        doc.insert()
        doc.submit()
        count1 = frappe.db.count(
            "Service Invoice",
            {"job_card": doc.name}
        )
        doc.on_submit()
        count2 = frappe.db.count(
            "Service Invoice",
            {"job_card": doc.name}
        )
        self.assertEqual(count1, count2)