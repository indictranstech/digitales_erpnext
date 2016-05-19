// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// Module CRM

cur_frm.cscript.tname = "Sales Order Item";
cur_frm.cscript.fname = "sales_order_details";
cur_frm.cscript.other_fname = "other_charges";
cur_frm.cscript.sales_team_fname = "sales_team";

cur_frm.add_fetch('item_code','product_release_date','release_date_of_item');
cur_frm.add_fetch('customer','customer_group','customer_group');
cur_frm.add_fetch('customer','territory','territory');
// cur_frm.add_fetch('customer','tender_group','tender_group');

{% include 'digitales/add_artist.js'%}
{% include 'selling/sales_common.js' %}
{% include 'accounts/doctype/sales_taxes_and_charges_master/sales_taxes_and_charges_master.js' %}
{% include 'accounts/doctype/sales_invoice/pos.js' %}

erpnext.selling.SalesOrderController = erpnext.selling.SellingController.extend({
	refresh: function(doc, dt, dn) {
		this._super();
		this.frm.dashboard.reset();
		if(!doc.delivery_date){ //Newly added
			doc.delivery_date = doc.transaction_date
			refresh_field('delivery_date')
		}

		if(doc.docstatus==1) {
			if(doc.status != 'Stopped') {


				cur_frm.dashboard.add_progress(cint(doc.per_delivered) + __("% Delivered"),
					doc.per_delivered);
				cur_frm.dashboard.add_progress(cint(doc.per_billed) + __("% Billed"),
					doc.per_billed);

				// delivery note
				if(flt(doc.per_delivered, 2) < 100 && ["Sales", "Shopping Cart"].indexOf(doc.order_type)!==-1)
					cur_frm.add_custom_button(__('Make Delivery'), this.make_delivery_note, "icon-truck");

				// indent
				if(!doc.order_type || ["Sales", "Shopping Cart"].indexOf(doc.order_type)!==-1)
					cur_frm.add_custom_button(__('Make ') + __('Material Request'),
						this.make_material_request, "icon-ticket");

				// sales invoice
				if(flt(doc.per_billed, 2) < 100) {
					cur_frm.add_custom_button(__('Make Invoice'), this.make_sales_invoice,
						frappe.boot.doctype_icons["Sales Invoice"]);
				}

				// stop
				if(flt(doc.per_delivered, 2) < 100 || flt(doc.per_billed,2) < 100)
					cur_frm.add_custom_button(__('Stop'), cur_frm.cscript['Stop Sales Order'],
						"icon-exclamation", "btn-default")




				//added by pitambar
				// if(flt(doc.per_delivered, 2) < 100 || doc.per_billed < 100)
				// 	cur_frm.add_custom_button(__('Stop Item'), cur_frm.cscript['Stop Sales Order Item'],
				// 		"icon-exclamation", "btn-default")




						// maintenance
						if(flt(doc.per_delivered, 2) < 100 && ["Sales", "Shopping Cart"].indexOf(doc.order_type)===-1) {
							cur_frm.add_custom_button(__('Make Maint. Visit'),
								this.make_maintenance_visit, null, "btn-default");
							cur_frm.add_custom_button(__('Make Maint. Schedule'),
								this.make_maintenance_schedule, null, "btn-default");
						}

				cur_frm.add_custom_button(__('Send SMS'), cur_frm.cscript.send_sms, "icon-mobile-phone", true);

			} else {
				// un-stop
				cur_frm.dashboard.set_headline_alert(__("Stopped"), "alert-danger", "icon-stop");
				cur_frm.add_custom_button(__('Unstop'), cur_frm.cscript['Unstop Sales Order'], "icon-check");
			}
		}

		if (this.frm.doc.docstatus===0) {
			cur_frm.add_custom_button(__('From Quotation'),
				function() {
					frappe.model.map_current_doc({
						method: "erpnext.selling.doctype.quotation.quotation.make_sales_order",
						source_doctype: "Quotation",
						get_query_filters: {
							docstatus: 1,
							status: ["!=", "Lost"],
							order_type: cur_frm.doc.order_type,
							customer: cur_frm.doc.customer || undefined,
							company: cur_frm.doc.company
						}
					})
				}, "icon-download", "btn-default");
		}

		this.order_type(doc);
	},

	order_type: function() {
		this.frm.toggle_reqd("delivery_date", this.frm.doc.order_type == "Sales");
	},

	tc_name: function() {
		this.get_terms();
	},

	customer: function(){
		return frappe.call({
			method: "erpnext.selling.doctype.customer.customer.get_contract_details",
			args: {
				"customer": cur_frm.doc.customer
			},
			callback: function(r) {
				if(r.message){
					cur_frm.doc.tender_group = r.message.tender_group;
					cur_frm.refresh_fields();
				}
			}
		});
	},

	warehouse: function(doc, cdt, cdn) {
		var item = frappe.get_doc(cdt, cdn);
		if(item.item_code && item.warehouse) {
			return this.frm.call({
				method: "erpnext.stock.get_item_details.get_available_qty",
				child: item,
				args: {
					item_code: item.item_code,
					warehouse: item.warehouse,
				},
			});
		}
	},

	
	make_material_request: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_material_request",
			frm: cur_frm
		})
	},

	make_delivery_note: function() {

		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note",
			frm: cur_frm
		})
	},
	
	make_sales_invoice: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
			frm: cur_frm
		})
	},

	make_maintenance_schedule: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_maintenance_schedule",
			frm: cur_frm
		})
	},

	make_maintenance_visit: function() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_maintenance_visit",
			frm: cur_frm
		})
	},
});

// for backward compatibility: combine new and previous states
$.extend(cur_frm.cscript, new erpnext.selling.SalesOrderController({frm: cur_frm}));

cur_frm.cscript.new_contact = function(){
	tn = frappe.model.make_new_doc_and_get_name('Contact');
	locals['Contact'][tn].is_customer = 1;
	if(doc.customer) locals['Contact'][tn].customer = doc.customer;
	loaddoc('Contact', tn);
}


cur_frm.fields_dict['project_name'].get_query = function(doc, cdt, cdn) {
	return {
		query: "erpnext.controllers.queries.get_project_name",
		filters: {
			'customer': doc.customer
		}
	}
}

cur_frm.cscript['Stop Sales Order'] = function() {
	var doc = cur_frm.doc;
	var check = confirm(__("Are you sure you want to STOP ") + doc.name);

	if (check) {
		return $c('runserverobj', {
			'method':'stop_sales_order',
			'docs': doc
			}, function(r,rt) {
			cur_frm.refresh();
		});
	}
}



cur_frm.cscript['Unstop Sales Order'] = function() {
	var doc = cur_frm.doc;

	var check = confirm(__("Are you sure you want to UNSTOP ") + doc.name);

	if (check) {
		return $c('runserverobj', {
			'method':'unstop_sales_order',
			'docs': doc
		}, function(r,rt) {
			cur_frm.refresh();
		});
	}
}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	if(cint(frappe.boot.notification_settings.sales_order)) {
		cur_frm.email_doc(frappe.boot.notification_settings.sales_order_message);
	}
	cur_frm.reload_doc()
};

cur_frm.cscript.send_sms = function() {
	frappe.require("assets/erpnext/js/sms_manager.js");
	var sms_man = new SMSManager(cur_frm.doc);
};


cur_frm.cscript.customer = function(doc, cdt, cdn){
	//var d = locals[cdt][cdn];
	if (doc.customer){
		var someDate = new Date();
		var numberOfDaysToAdd = 6;
		someDate.setDate(someDate.getDate() + numberOfDaysToAdd); 
		var dd = someDate.getDate();
		var mm = someDate.getMonth() + 1;
		var y = someDate.getFullYear();
		var someFormattedDate = y + '-'+ mm + '-'+ dd;
		cur_frm.set_value('delivery_date',someFormattedDate)
		refresh_field('delivery_date')
	}
	refresh_field('amount');
}

cur_frm.get_field("budget").get_query=function(doc,cdt,cdn){
	if (doc.customer){
 		{
    		return "select budget from `tabBudget Details` where parent='"+doc.customer+"'"

 		}
 	}
 	else
 		msgprint("First select the customer")
}
cur_frm.cscript.priority = function(doc, cdt, cdn){
	//var d = locals[cdt][cdn];

	if (doc.priority){
		var someDate = new Date();
		var numberOfDaysToAdd = 6;
		someDate.setDate(someDate.getDate() + numberOfDaysToAdd); 
		var dd = someDate.getDate();
		var mm = someDate.getMonth() + 1;
		var y = someDate.getFullYear();
		var someFormattedDate = y + '-'+ mm + '-'+ dd;
		cur_frm.set_value('delivery_date',someFormattedDate)
		refresh_field('delivery_date')
	}
	refresh_field('amount');
}


cur_frm.fields_dict.billing_address_name.get_query=function(doc,cdt,cdn){
	return{
		filters: {
			'customer':doc.customer,
			'address_type':'Billing'
		}
	}
}

cur_frm.cscript.shipping_address_name.get_query=function(doc,cdt,cdn){
	return{
		filters: {
			'customer':doc.customer,
			'address_type':'Shipping'
		}
	}
}

cur_frm.cscript.sales_person = function(doc,cdt, cdn){
	d = locals[cdt][cdn].allocated_percentage = 100;
	cur_frm.refresh_field("sales_team");
}

{% include 'digitales/custom_js_methods.js' %}
$.extend(cur_frm.cscript, new erpnext.selling.CustomSalesOrder());