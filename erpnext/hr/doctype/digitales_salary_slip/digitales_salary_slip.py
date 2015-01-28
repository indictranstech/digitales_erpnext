# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, cint, cstr, flt, getdate, nowdate, rounded
from frappe.model.naming import make_autoname

from frappe import msgprint, _
from erpnext.setup.utils import get_company_currency
from erpnext.hr.utils import set_employee_name
import datetime
from datetime import date, timedelta

from erpnext.utilities.transaction_base import TransactionBase

class DigitalesSalarySlip(Document):
	pass


	def get_weeklyofday_details(self,args):
		frappe.errprint("in the py")
		# frappe.errprint(args['from_date'])
		# frappe.errprint(args['to_date'])
		#salary_slip=self.get_salary_slip(self.from_date)
		holidays = self.get_holidays_for_employee(args)
		self.total_days_in_month=14-len(holidays)
		# self.total_days_in_month=14

	def get_salary_slip(self,from_date):
		frappe.errprint("in get salary slip")
		salary_slip=frappe.db.sql("""select name from `tabDigitales Salary Slip` where employee='%s'
				and to_date>'%s' and docstatus=0 or docstatus=1"""%(self.employee,from_date))
		#frappe.errprint(salary_slip)

		if salary_slip:
			dates=frappe.db.sql("""select from_date,to_date from `tabDigitales Salary Slip`
			  where name='%s'"""%salary_slip[0][0])
			#frappe.errprint(dates[0][0])
			frappe.msgprint("Salary Slip is already generated for the employee='"+self.employee+"' for dates from date='%s' and to date='%s'"%(dates[0][0],dates[0][1]))

	def get_holidays_for_employee(self,m):
		frappe.errprint("get_holidays_for_employee")

		holidays = frappe.db.sql("""select t1.holiday_date
			from `tabHoliday` t1, tabEmployee t2
			where t1.parent = t2.holiday_list and t2.name = %s
			and t1.holiday_date between %s and %s""",
			(m['employee'], m['month_start_date'], m['month_end_date']))
		if not holidays:
			holidays = frappe.db.sql("""select t1.holiday_date
				from `tabHoliday` t1, `tabHoliday List` t2
				where t1.parent = t2.name and ifnull(t2.is_default, 0) = 1
				and t2.fiscal_year = %s
				and t1.holiday_date between %s and %s""", (self.fiscal_year,
					m['month_start_date'], m['month_end_date']))
		holidays = [cstr(i[0]) for i in holidays]
		return holidays



	def get_emp_and_leave_details(self):
		frappe.errprint("in the")
		if self.employee:
			#salary_slip=self.get_salary_slip(self.from_date)
			self.get_leave_details()
			salary_structure=frappe.db.sql("""select digitales_salary_structure from `tabEmployee`
						where name='%s'"""%self.employee)
			if salary_structure[0][0]=='Yes':

				struct = self.check_sal_struct()
				if struct:
					self.pull_sal_struct(struct)

			elif salary_structure[0][0]=='No':
				rate=frappe.db.get_value("Employee",self.employee ,"hour_rate")
				frappe.errprint(rate)
				frappe.db.set(self, 'hour_rate', rate)
				frappe.errprint(self.attendance_hours)
				if rate:
					self.create_sal_stucture(rate,self.attendance_hours)	
				else:
					frappe.throw("Hour rate is not mentioned for the employee='"+self.employee+"' in employee master")

			else:
				frappe.throw("Digitales Salary Structure {Yes,No} is not specified in Employee master")


	def get_leave_details(self, lwp=None):
		frappe.errprint("in get leave details")
		if not self.fiscal_year:
			self.fiscal_year = frappe.get_default("fiscal_year")
		if not self.month:
			self.month = "%02d" % getdate(nowdate()).month

		"""code for holidays"""

		m={'employee':self.employee,'month_start_date': self.from_date,'month_end_date':self.to_date}
		frappe.errprint(m)
		holidays = self.get_holidays_for_employee(m)
		m["month_days"]=14


		if not cint(frappe.db.get_value("HR Settings", "HR Settings",
			"include_holidays_in_total_working_days")):
				frappe.errprint(["length",len(holidays)])
				m["month_days"] -= len(holidays)
				# week_days -= len(holidays)
				if m["month_days"] < 0:
					frappe.throw(_("There are more holidays than working days this month."))

		if not lwp:
			lwp = self.calculate_lwp(holidays, m)
			frappe.errprint(["lwp",lwp])
			frappe.errprint(["month_days",m['month_days']])
		self.total_days_in_month = m['month_days']
		#frappe.errprint(["total_days_in_month",total_days_in_month])
		self.leave_without_pay = lwp
		#frappe.errprint(["leave_without_pay",leave_without_pay])
		payment_days = flt(self.get_payment_days(m)) - flt(lwp)
		# payment_days = flt(self.total_days_in_month) - flt(lwp)
		attendance_days,attendance_hours= self.get_attendance_days()
		self.attendance_days = attendance_days 
		self.attendance_hours = attendance_hours
		frappe.errprint(["payment_days",payment_days])
		self.payment_days = payment_days > 0 and payment_days or 0


	def calculate_lwp(self, holidays, m):
		lwp = 0
		for d in range(m['month_days']):
			dt = add_days(cstr(m['month_start_date']), d)
			if dt not in holidays:
				leave = frappe.db.sql("""
					select t1.name, t1.half_day
					from `tabLeave Application` t1, `tabLeave Type` t2
					where t2.name = t1.leave_type
					and ifnull(t2.is_lwp, 0) = 1
					and t1.docstatus = 1
					and t1.employee = %s
					and %s between from_date and to_date
				""", (self.employee, dt))
				if leave:
					lwp = cint(leave[0][1]) and (lwp + 0.5) or (lwp + 1)
		return lwp


	def get_payment_days(self, m):
		frappe.errprint("get_payment_days")
		# frappe.errprint([getdate(emp['date_of_joining']).day + 1])
		payment_days = m['month_days']
		emp = frappe.db.sql("select date_of_joining, relieving_date from `tabEmployee` \
			where name = %s", self.employee, as_dict=1)[0]
		frappe.errprint(emp)
		frappe.errprint([getdate(emp['date_of_joining']).day + 1])
		# frappe.errprint([getdate(emp['relieving_date']).day])
		if emp['relieving_date']:
			if getdate(emp['relieving_date']) > getdate(m['month_start_date']) and \
				getdate(emp['relieving_date']) < getdate(m['month_end_date']):
					payment_days = getdate(emp['relieving_date']).day
			elif getdate(emp['relieving_date']) < getdate(m['month_start_date']):
				frappe.throw(_("Employee relieved on {0} must be set as 'Left'").format(emp["relieving_date"]))

		if emp['date_of_joining']:
			frappe.errprint(type(emp['date_of_joining']))
			frappe.errprint(type(m['month_start_date']))
			if getdate(emp['date_of_joining']) > getdate(m['month_start_date']) and \
				getdate(emp['date_of_joining']) < getdate(m['month_end_date']):
					payment_days = payment_days - getdate(emp['date_of_joining']).day + 1
			elif getdate(emp['date_of_joining']) > getdate(m['month_end_date']):
				payment_days = 0

		return payment_days


	def get_attendance_days(self):
		frappe.errprint("in attendance days")
		#d = getdate(self.to_date)- timedelta(days=1)
		# frappe.errprint(d)
		att_dates=frappe.db.sql("""select count(att_date),ifnull(sum(total_hours),0)from `tabAttendance` where docstatus=1 and status='Present'
						and employee='%s' and att_date between '%s' and '%s'"""%(self.employee,self.from_date,self.to_date),debug=1)
		frappe.errprint(att_dates)
		if att_dates:

			attendance_days=att_dates[0][0]
			attendance_hours=att_dates[0][1]

		att_dates1=frappe.db.sql("""select count(att_date) ,ifnull(sum(total_hours),0) from `tabAttendance` where docstatus=1 and status='Half Day' 
						and employee='%s' and att_date between '%s' and '%s'"""%(self.employee,self.from_date,self.to_date),debug=1)
		frappe.errprint(att_dates1)
		if att_dates1:
			attendance_days=att_dates[0][0] + (att_dates1[0][0]*0.5)
			attendance_hours=attendance_hours + att_dates1[0][1]
			if attendance_days > 0 and attendance_hours > 0:

				return attendance_days,attendance_hours
			else:

				frappe.throw("There is no any attendance marked for the employee='%s' for the dates in between,from date='%s' and to date='%s'"%(self.employee,self.from_date,self.to_date))


		if  attendance_day >0 and attendance_hours >0:

			return attendance_days,attendance_hours
		else:
			frappe.throw("There is no any attendance marked for the employee='%s' for the dates in between,from date='%s' and to date='%s'"%(self.employee,self.from_date,self.to_date))

	def check_sal_struct(self):
		struct = frappe.db.sql("""select name from `tabSalary Structure`
			where employee=%s and is_active = 'Yes'""", self.employee)
		if not struct:
			msgprint(_("Please create Salary Structure for employee {0}").format(self.employee))
			self.employee = None
		return struct and struct[0][0] or ''




	def pull_sal_struct(self, struct):
		frappe.errprint("in the pull_sal_struct")
		from erpnext.hr.doctype.salary_structure.salary_structure import make_salary_slip
		earning= frappe.db.sql(""" select  e_type,modified_value from `tabSalary Structure Earning` where 
					parent='%s'"""%struct,as_dict=1)
		frappe.errprint(earning)
		if earning:
			self.set('earning_details', [])
			for i in earning:
				e = self.append('earning_details', {})
				e.e_modified_amount=i['modified_value']
				e.e_amount=i['modified_value']
				e.e_depends_on_lwp=1
				e.e_type=i['e_type']
			
		deduction=frappe.db.sql(""" select  d_type,d_modified_amt from `tabSalary Structure Deduction` where 
					parent='%s'"""%struct,as_dict=1)
		frappe.errprint(deduction)
		if deduction:
			self.set('deduction_details', [])
			for j in deduction:
				d = self.append('deduction_details', {})
				d.d_modified_amount=j['d_modified_amt']
				d.d_amount=j['d_modified_amt']
				d.d_depends_on_lwp=1
				d.d_type=j['d_type']

	def create_sal_stucture(self,rate,hour):
		frappe.errprint("in create_sal_stucture")
		self.set('earning_details', [])
		e = self.append('earning_details', {})
		e.e_modified_amount=rate*hour
		e.e_amount=rate*hour
		e.e_type= 'Basic'
			
	def pull_emp_details(self):
		emp = frappe.db.get_value("Employee", self.employee,
			["bank_name", "bank_ac_no"], as_dict=1)
		if emp:
			self.bank_name = emp.bank_name
			self.bank_account_no = emp.bank_ac_no

	

	def validate(self):
		# frappe.errprint("in the validate")
		from frappe.utils import money_in_words
		self.check_existing()
		#self.validate_attendance()
		if not (len(self.get("earning_details")) or
			len(self.get("deduction_details"))):
				self.get_emp_and_leave_details()
		else:
			self.get_leave_details(self.leave_without_pay)

		if not self.net_pay:
			self.calculate_net_pay()

		company_currency = get_company_currency(self.company)
		#frappe.errprint(company_currency)
		self.total_in_words = money_in_words(self.rounded_total, company_currency)
		#frappe.errprint(self.total_in_words)
		set_employee_name(self)
		


	def check_existing(self):
		frappe.errprint("check_existing")
		ret_exist = frappe.db.sql("""select name from `tabDigitales Salary Slip`
			where (from_date between %s and %s or to_date between %s and %s) and fiscal_year = %s and docstatus != 2
			and employee = %s and name != %s""",
			(self.from_date, self.to_date,self.from_date,self.to_date,self.fiscal_year, self.employee, self.name),debug=1)
		frappe.errprint(ret_exist)
		if ret_exist:
			dates=frappe.db.sql("""select from_date,to_date from `tabDigitales Salary Slip`
			  where name='%s'"""%ret_exist[0][0])
			#self.employee = ''
			frappe.throw("Salary Slip of employee='%s' already created for the dates from date='%s' and to date='%s'"%(self.employee,dates[0][0],dates[0][1]))
	
	def calculate_earning_total(self):
		self.gross_pay = flt(self.arrear_amount) + flt(self.leave_encashment_amount)
		for d in self.get("earning_details"):
			if cint(d.e_depends_on_lwp) == 1:
				d.e_modified_amount = rounded(flt(d.e_amount) * flt(self.payment_days)
					/ cint(self.total_days_in_month), 2)
			elif not self.payment_days:
				d.e_modified_amount = 0
			else:
				d.e_modified_amount = d.e_amount
			self.gross_pay += flt(d.e_modified_amount)

	def calculate_ded_total(self):
		self.total_deduction = 0
		for d in self.get('deduction_details'):
			if cint(d.d_depends_on_lwp) == 1:
				d.d_modified_amount = rounded(flt(d.d_amount) * flt(self.payment_days)
					/ cint(self.total_days_in_month), 2)
			elif not self.payment_days:
				d.d_modified_amount = 0
			else:
				d.d_modified_amount = d.d_amount

			self.total_deduction += flt(d.d_modified_amount)

	def calculate_net_pay(self):
		self.calculate_earning_total()
		self.calculate_ded_total()
		self.net_pay = flt(self.gross_pay) - flt(self.total_deduction)
		self.rounded_total = rounded(self.net_pay)


	def validate_attendance(self):
		#d = getdate(self.to_date)- timedelta(days=1)
		# frappe.errprint(d)
		att_dates=frappe.db.sql("""select count(att_date) from `tabAttendance` where docstatus=1 and status='Present' 
						and employee='%s' and att_date between '%s' and '%s'"""%(self.employee,self.from_date,self.to_date),debug=1)
		# frappe.errprint(att_dates)
		if att_dates:
			frappe.throw("Total payment days for employee='%s' is '%s' and total attendance for the specified dates is '%s'"%(self.employee,self.payment_days,att_dates[0][0]))


	def on_submit(self):
		if(self.email_check == 1):
			self.send_mail_funct()


	def send_mail_funct(self):
		from frappe.utils.email_lib import sendmail

		receiver = frappe.db.get_value("Employee", self.employee, "company_email")
		frappe.errprint(receiver)
		if receiver:
			subj = 'Salary Slip - ' + cstr(self.from_date) +'/'+cstr(self.to_date) 
			sendmail([receiver], subject=subj, msg = _("Please see attachment"),
				attachments=[{
					"fname": self.name + ".pdf",
					"fcontent": frappe.get_print_format(self.doctype, self.name, as_pdf = True)
				}])
		else:
			msgprint(_("Company Email ID not found, hence mail not sent"))
