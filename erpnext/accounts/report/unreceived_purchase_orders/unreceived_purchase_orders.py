# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	item_details=get_item_conditions(filters)
	data = []
	sl_entries = get_sales_order_details(filters)
	item_details=get_item_conditions(filters)
	return columns, sl_entries


def get_columns():
	return [_("Order Name") + ":Link/Sales Order:130",_("Customer") + ":Link/Customer:130",_("Item") + ":Link/Item:130",
	 _("Item Name") + "::100", _("Item Group") + ":Link/Item Group:100",
		 _("Description") + "::200",_("Item Release Date") + ":Datetime:95",
		 _("Quantity Ordered") + ":Float:50",_("Assigned Qty") + ":Float:50",_("Qty In Stock") + ":Float:50",
		 _("RRP") + ":Link/Price List:50",_("Budget") + ":Link/Budget:100",
		 _("RRP Excluding GST") + ":Float:50",_("Order Type") + "::50",
		  _("Status") + "::50",
		 _("Gross Amount") + ":Currency:50",
		 _("Quantity Invoiced") + ":Float:50",
		  _("Service Type") + ":Float:50"]
		
		

def get_sales_order_details(filters):
	return frappe.db.sql("""select so.name, so.customer,soi.item_code,soi.item_name,
		soi.item_group,soi.description,soi.release_date_of_item,soi.qty,soi.assigned_qty,
		soi.actual_qty,
		soi.rrp,soi.budget,soi.gst_value,so.order_type,so.status,
		so.grand_total_export
		 from `tabSales Order` so,
		`tabSales Order Item` soi where 
		so.name=soi.parent and soi.assigned_qty<>soi.actual_qty 
		%s """%get_item_conditions(filters),as_list=1)


def get_item_conditions(filters):
	conditions = []
	if filters.get("customer"):
		conditions.append("customer='%(customer)s'"%filters)
	if filters.get("item_group"):
		conditions.append("item_group='%(item_group)s'"%filters)
	if filters.get("budget"):
		conditions.append("budget='%(budget)s'"%filters)
	if filters.get("order_type"):
		conditions.append("order_type='%(order_type)s'"%filters)
	if filters.get("service_type"):
		conditions.append("service_type='%(service_type)s'"%filters)

	return " and "+" and ".join(conditions) if conditions else ""