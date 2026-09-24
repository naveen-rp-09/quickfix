// Copyright (c) 2026, quickfix and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Job Card", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Job Card', {
	setup(frm) {
        frm.set_query("assigned_technician", function() {
            return {
                filters: {
                    status: "Active",
                    specialization: frm.doc.device_type
                }
            };
        });
    },

	refresh(frm) {

        frm.set_value("labour_charge",500)

        if (!frappe.user.has_role("QF Manager")) {
                 frm.set_df_property("customer_phone", "hidden", 1);
        }
        else {
        frm.set_df_property("customer_phone", "hidden", 0);
        }

		
		const status_colors={
		     "Draft":"Grey",
             "Pending Diagnosis":"Orange",
             "Awaiting Customer Approval":"Yellow",
             "In Repair":"Blue",
             "ReadyforDelivery":"Green",
             "Delivered":"Green",
             "Cancelled":"Red"   
		};
		 if (frm.doc.status) {
            frm.dashboard.add_indicator(
                frm.doc.status,
                status_colors[frm.doc.status] || "gray"
            );
        }
		
		if (frm.doc.status === "Ready for Delivery" && frm.doc.docstatus === 1 ){    
		frm.add_custom_button("Mark as Delivered",function(){
		    frm.set_value(
		        "status",
		        "Delivered"
		        );
		        frm.save();
		    }
		  );
		}

        frm.add_custom_button("Reject Job",function(){
		    let dialog = new frappe.ui.Dialog({
		        title:'Rejecting Job Card',
		        fields: [
                    {
                     label: 'Rejection Reason',
                     fieldname: 'rejection_reason',
                     fieldtype: 'Data',
                     reqd:1
                   }
                ],
                primary_action_label:"Reject",
                 primary_action(values){
                     frm.set_value(
                         "remarks",values.rejection_reason)
                     frm.set_value(
                         "status","Cancelled") 
                     dialog.hide();
                     frm.save();
                }
		    }) 
		    dialog.show();
		});

        	frm.add_custom_button("Transfer Technician", function() {
            frappe.prompt(
                [
                   {
                        label: "New Technician",
                        fieldname: "new_technician",
                        fieldtype: "Link",
                        options: "Technician",
                        reqd: 1
                    }
                ],

                function(values) {
                    frappe.confirm(
                        "Are you want to transfer the technician",
                        function() {
                            frappe.call({
                                method: "quickfix.api.transfer_job",
                                args: {
                                    from_tech:
                                        frm.doc.technician,
                                    to_tech:
                                        values.new_technician
                                },
                                callback: function(r) {
                                    if (!r.exc) {
                                        frm.set_value(
                                            "technician",
                                            values.new_technician
                                        );
                                        frm.trigger(
                                            "technician"
                                        );
                                    }
                                }
                            });
                        }
                    );
                },
                "Transfer Technician",
                "Transfer"
            );
        });	
	},

technician(frm){
    if(!frm.doc.technician)
       return;
       
    if (!frm.doc.device_type)
       return;
       
    frappe.db.get_value(
        "Technician",
        frm.doc.technician,
        "specialization"
        ).then(function(r){
            if(!r.message){
                return;
            }
            const specialization = r.message.specialization;
            
            if(specialization && specialization!=frm.doc.device_type){
                frappe.msgprint({
                   title:"Invalid Technician",                    
                   message:"Technician mismatch so check it once",
                   indicator:"orange" 
                });
            }
            
        });  
    }

//  parts_used_remove(frm){
//        calculate_rowtotal(frm,cdt,cdn)
//     }
    
});

function calculate_rowtotal(frm, cdt, cdn) {

    let row = locals[cdt][cdn];
    let quantity = row.quantity || 0;
    let unit_price = row.unit_price || 0;
    let total_price = quantity * unit_price;
    frappe.model.set_value(
        cdt,
        cdn,
        "total_price",
        total_price
    );
    calculate_parts_total(frm);
}


function calculate_parts_total(frm) {
    let total = 0;
    (frm.doc.parts_used || []).forEach(row => {
        let quantity = row.quantity || 0;
        let unit_price = row.unit_price || 0;
        let row_total = quantity * unit_price;
        total += row_total;
    });
    frm.set_value(
        "parts_total",
        total
    );
    default_labour_amount(frm)
    calculate_final_amount(frm);
}

function default_labour_amount(frm){
   frm.set_value("labour_charge",500)
}

function calculate_final_amount(frm) {
    let parts_total = frm.doc.parts_total || 0;
    let labour_charge = frm.doc.labour_charge || 0;
    let final_amt = parts_total + labour_charge;
    frm.set_value(
        "final_amount",
        final_amt
    );
}

frappe.ui.form.on('Part Usage Entry', {
    quantity(frm, cdt, cdn) {
        calculate_rowtotal(
            frm,
            cdt,
            cdn
        );
    },
    unit_price(frm, cdt, cdn) {
        calculate_rowtotal(
            frm,
            cdt,
            cdn
        );
    }
});

// #old
// function calculate_rowtotal(frm,cdt,cdn){
//         let row = locals[cdt][cdn]
//         total_price=0
//         total=0
//         (frm.doc.parts_used or []).forEach(row => {
//              total_price=(row.quantity || 0)*(row.unit_price || 0)
//              frappe.model.set_value(
//                 cdt,
//                 cdn,
//                 "total_price",total_price
//             )
//             total+=total_price
//         });
        
        
//         frm.set_value("parts_total",total)
//         parts_total(frm)    
//     }

// function parts_total(frm){
//     final_amt = 0
//     final_amt = frm.doc.parts_total + frm.doc.labour_charge
//     frm.set_value("final_amount",final_amt)
// }

// frappe.ui.form.on('Part Usage Entry',{
//     quantity(frm,cdt,cdn){
//        calculate_rowtotal(frm,cdt,cdn)
//     },
//     unit_price(frm,cdt,cdn){
//        calculate_rowtotal(frm,cdt,cdn)
//     }
// })