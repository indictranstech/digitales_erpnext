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
	return [_("Customer") + ":Link/Customer:200",_("Tender Group") + ":Link/Tender Group:200", _("Monthly Spend") + ":Currency:200"]
	
def get_sales_invoice_details(filters):
	return frappe.db.sql(""" select customer,tender_group, grand_total_export from `tabSales Invoice`
							where posting_date between %(from_date)s and %(to_date)s {sle_conditions} """\
							.format(sle_conditions=get_item_conditions(filters)), filters, as_list=1,debug=1)

def get_item_conditions(filters):
	conditions = []
	if filters.get("tender_group"):
		conditions.append("tender_group='%(tender_group)s'"%filters)
	if filters.get("customer"):
		conditions.append("customer='%(customer)s'"%filters)

	return " and {}".format(" and ".join(conditions)) if conditions else ""