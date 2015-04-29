// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
// For license information, please see license.txt

frappe.query_reports["Spend By Item By Customer"] = {
	"filters": [
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"options": "From Date"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"options": "To Date"
		},
		{
			"fieldname":"item_group",
			"label": __("Media"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
		{
			"fieldname":"budget",
			"label": __("Budget"),
			"fieldtype": "Link",
			"options": "Budget"
		},
		{
			"fieldname":"new_order_type",
			"label": __("Order Type"),
			"fieldtype": "Select",
			"options": "\nStandard Order\nStanding Order\nReader Request"
		},
		/*{
			"fieldname":"service_type",
			"label": __("Service Type"),
			"fieldtype": "Data"
			//"options": "Sales\nMaintenance\nShopping Cart"
		}*/
	]
}
