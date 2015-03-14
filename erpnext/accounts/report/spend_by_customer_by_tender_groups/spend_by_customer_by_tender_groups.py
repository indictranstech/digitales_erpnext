# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	item_details=get_item_conditions(filters)
	sl_entries = get_sales_invoice_details(filters)
	#frappe.errprint(sl_entries)
	
	data = []
	fiscal_year = frappe.db.get_value('Global Defaults', None, 'current_fiscal_year')
	fiscal_year_start_date = frappe.db.get_value('Fiscal Year', fiscal_year, 'year_start_date')
	
	return columns, sl_entries


def get_columns():
	return [_("Customer") + ":Link/Customer:130",_("Tender Group") + ":Link/Tender Group:130", _("Item Name") + "::100",_("Monthly Spend") + ":Currency:100"]
	
def get_sales_invoice_details(filters):
	pass	 

def get_item_conditions(filters):
	conditions = []
	if filters.get("tender_group"):
		conditions.append("tender_group='%(budget)s'"%filters)
	if filters.get("customer"):
		conditions.append("customer='%(order_type)s'"%filters)

	return " and "+" and ".join(conditions) if conditions else ""