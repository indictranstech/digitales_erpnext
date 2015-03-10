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
	return [_("Customer") + ":Link/Customer:130",_("Item") + ":Link/Item:130", _("Item Name") + "::100", _("Item Group") + ":Link/Item Group:100",
		 _("Description") + "::200",_("Qty") + ":Float:50", _("Budget") + ":Link/Budget:100", _("Order Type") + ":Data:100",
		_("Price") + ":Currency:110", _("Monthly Spend") + ":Currency:110", _("YTD Spend Including Current Month") + ":Currency:110",
		_("Invoice Number") + "::110", _("Invoice Date") + ":Datetime:95"]


def get_sales_invoice_details(filters):
	return frappe.db.sql("""SELECT foo.customer_name, foo.item_code,foo.item_name,foo.item_group,
		foo.description,foo.quantity,foo.budget,foo.order_type,
		foo.price,foo.amount,foo.monthly_spend,foo.invoice_number,foo.posting_date,
		sum(case when month(posting_date)=month(now()) then foo.amount else 0 end) as month_sum,sum(foo.amount) as year_sum 
from(
SELECT
    a.customer_name as customer_name,
    b.item_code as item_code,
    b.item_name as item_name,
    b.item_group as item_group,
    b.description as description,
    b.qty as quantity,
    b.budget as budget,
    a.order_type as order_type,
    b.rate as price,
    b.amount as amount,
    b.amount as monthly_spend,
    a.name as invoice_number,
    a.posting_date as posting_date 
FROM
    `tabSales Invoice` a,
    `tabSales Invoice Item` b
WHERE
    b.parent = a.name
    %s
) as foo group by foo.customer_name, foo.item_code"""%get_item_conditions(filters),as_list=1)
			

def get_item_conditions(filters):
	conditions = []
	if filters.get("budget"):
		conditions.append("budget='%(budget)s'"%filters)
	if filters.get("order_type"):
		conditions.append("order_type='%(order_type)s'"%filters)
	if filters.get("service_type"):
		conditions.append("service_type='%(service_type)s'"%filters)

	return " and "+" and ".join(conditions) if conditions else ""