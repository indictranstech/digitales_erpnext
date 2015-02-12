# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt
from frappe.model.document import Document
from frappe import _


class DigitalesSalaryManager(Document):
	

	def get_emp_list(self):
		#frappe.errprint("1. in get employee list")
		"""
			Returns list of active employees based on selected criteria
			and for which salary structure exists
		"""

		cond = self.get_filter_condition()
		cond += self.get_joining_releiving_condition()

		emp_list=frappe.db.sql("""select t1.name from `tabEmployee` t1
				where t1.status='Active' and t1.docstatus!=2 %s"""%cond,debug=1)

		# emp_list = frappe.db.sql("""
		# 	select t1.name
		# 	from `tabEmployee` t1, `tabSalary Structure` t2
		# 	where t1.docstatus!=2 and t2.docstatus != 2
		# 	and t1.name = t2.employee and t1.digitales_salary_structure='Yes'
		# %s """% cond,debug=1)
		frappe.errprint(emp_list)
		return emp_list


	def get_filter_condition(self):
		#frappe.errprint("2. in get get_filter_condition")
		self.check_mandatory()

		cond = ''
		for f in ['company', 'branch', 'department', 'designation']:
			if self.get(f):
				cond += " and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"

		

		return cond


	def get_joining_releiving_condition(self):
		#frappe.errprint("4. in get get_joining_releiving_condition")
		#m = self.get_month_details(self.fiscal_year, self.from_date,self.to_date)
		#frappe.errprint(["joining",m])
		cond = """
			and ifnull(t1.date_of_joining, '0000-00-00') <= '%s'
			and ifnull(t1.relieving_date, '2199-12-31') >= '%s'
		""" %(self.to_date,self.from_date)
		#frappe.errprint(cond)
		return cond


	def check_mandatory(self):
		#frappe.errprint("3. in check_mandatory")
		for f in ['company', 'fiscal_year']:
			if not self.get(f):
				frappe.throw(_("Please set {0}").format(f))


	# def get_month_details(self, year, from_date,to_date):
	# 	frappe.errprint("5 . get get_month_details")
	# 	ysd = frappe.db.get_value("Fiscal Year", year, "year_start_date")
	# 	if ysd:
	# 		from dateutil.relativedelta import relativedelta
	# 		import calendar, datetime
	# 		diff_mnt = cint(month)-cint(ysd.month)
	# 		if diff_mnt<0:
	# 			diff_mnt = 12-int(ysd.month)+cint(month)
	# 		msd = ysd + relativedelta(months=diff_mnt) # month start date
	# 		month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
	# 		med = datetime.date(msd.year, cint(month), month_days) # month end date
	# 		return {
	# 			'year': msd.year,
	# 			'month_start_date': msd,
	# 			'month_end_date': med,
	# 			'month_days': month_days
	# 		}

	def create_sal_slip(self):

		#frappe.errprint("0. create_sal_slip")
		"""
			Creates salary slip for selected employees if already not created

		"""

		emp_list = self.get_emp_list()
		ss_list = []
		for emp in emp_list:
			if not frappe.db.sql("""select name from `tabDigitales Salary Slip`
					where docstatus!= 2 and employee = %s and from_date=%s and to_date=%s and fiscal_year = %s and company = %s
					""", (emp[0], self.from_date,self.to_date, self.fiscal_year, self.company)):
				ss = frappe.get_doc({
					"doctype": "Digitales Salary Slip",
					"fiscal_year": self.fiscal_year,
					"employee": emp[0],
					"from_date": self.from_date,
					"to_date": self.to_date,
					"email_check": self.send_email,
					"company": self.company,
					"branch":self.branch,
					"department":self.department,
					"designation":self.designation,
				})
				frappe.errprint(ss)
				ss.insert()
				ss_list.append(ss.name)

		return self.create_log(ss_list)


	def create_log(self, ss_list):
		log = "<b>No employee for the above selected criteria OR salary slip already created</b>"
		if ss_list:
			log = "<b>Salary Slip has been created: </b>\
			<br><br>%s" % '<br>'.join(ss_list)
		return log


	def get_sal_slip_list(self):
		#frappe.errprint("2. get salary slip list")
		"""
			Returns list of salary slips based on selected criteria
			which are not submitted
		"""
		cond = self.get_filter_condition()
		frappe.errprint(cond)
		ss_list = frappe.db.sql("""
			select t1.name from `tabDigitales Salary Slip` t1
			where t1.docstatus = 0 and t1.from_date = %s and t1.to_date = %s and t1.fiscal_year = %s %s
		""" % ('%s', '%s','%s', cond), (self.from_date,self.to_date, self.fiscal_year),debug=1)
		return ss_list


	def submit_salary_slip(self):
		#frappe.errprint("1. submit salary slip")
		"""
			Submit all salary slips based on selected criteria
		"""
		ss_list = self.get_sal_slip_list()
		frappe.errprint([ss_list,"salary slip"])
		not_submitted_ss = []
		for ss in ss_list:
			ss_obj = frappe.get_doc("Digitales Salary Slip",ss[0])
			try:
				ss_obj.email_check = self.send_email
				ss_obj.submit()
			except Exception,e:
				not_submitted_ss.append(ss[0])
				frappe.msgprint(e)
				continue

		return self.create_submit_log(ss_list, not_submitted_ss)


	def create_submit_log(self, all_ss, not_submitted_ss):
		#frappe.errprint("3.create submit log")

		log = ''
		if not all_ss:
			log = "No salary slip found to submit for the above selected criteria"
		else:
			all_ss = [d[0] for d in all_ss]

		submitted_ss = list(set(all_ss) - set(not_submitted_ss))
		if submitted_ss:
			mail_sent_msg = self.send_email and " (Mail has been sent to the employee)" or ""
			log = """
			<b>Submitted Salary Slips%s:</b>\
			<br><br> %s <br><br>
			""" % (mail_sent_msg, '<br>'.join(submitted_ss))

		if not_submitted_ss:
			log += """
				<b>Not Submitted Salary Slips: </b>\
				<br><br> %s <br><br> \
				Reason: <br>\
				May be company email id specified in employee master is not valid. <br> \
				Please mention correct email id in employee master or if you don't want to \
				send mail, uncheck 'Send Email' checkbox. <br>\
				Then try to submit Salary Slip again.
			"""% ('<br>'.join(not_submitted_ss))
		return log


	def get_total_salary(self):
		#frappe.errprint("2. get_total_salary")
		"""
			Get total salary amount from submitted salary slip based on selected criteria
		"""
		cond = self.get_filter_condition()
		tot = frappe.db.sql("""
			select sum(rounded_total) from `tabDigitales Salary Slip` t1
			where t1.docstatus = 1 and from_date = %s and to_date = %s and fiscal_year = %s %s
		""" % ('%s', '%s','%s', cond), (self.from_date,self.to_date, self.fiscal_year),debug=1)

		return flt(tot[0][0])


	def get_acc_details(self):
		#frappe.errprint("1.get_acc_details")
		"""
			get default bank account,default salary acount from company
		"""
		amt = self.get_total_salary()
		default_bank_account = frappe.db.get_value("Company", self.company,
			"default_bank_account")
		if not default_bank_account:
			frappe.msgprint(_("You can set Default Bank Account in Company master"))

		return {
			'default_bank_account' : default_bank_account,
			'amount' : amt
		}
