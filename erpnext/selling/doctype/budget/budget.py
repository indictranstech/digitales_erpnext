# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import add_days, cint, cstr, flt, getdate, nowdate, rounded


class Budget(Document):
	pass

	def check_start_date(self,start_date):
		if start_date < nowdate():
			frappe.throw("Start date can not be greater than the current date")

	def check_end_date(self,end_date):
		if end_date < self.start_date:
			frappe.throw("End date must be less than the start date")