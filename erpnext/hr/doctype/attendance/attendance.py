# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, cint, cstr
from frappe.utils import getdate, nowdate
from frappe import _
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name

class Attendance(Document):
	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and att_date = %s
			and name != %s and docstatus = 1""",
			(self.employee, self.att_date, self.name))
		if res:
			frappe.throw(_("Attendance for employee {0} is already marked").format(self.employee))

		set_employee_name(self)

	def check_leave_record(self):
		if self.status == 'Present':
			leave = frappe.db.sql("""select name from `tabLeave Application`
				where employee = %s and %s between from_date and to_date and status = 'Approved'
				and docstatus = 1""", (self.employee, self.att_date))

			if leave:
				frappe.throw(_("Employee {0} was on leave on {1}. Cannot mark attendance.").format(self.employee,
					self.att_date))

	def validate_fiscal_year(self):
		from erpnext.accounts.utils import validate_fiscal_year
		validate_fiscal_year(self.att_date, self.fiscal_year)

	def validate_att_date(self):
		if getdate(self.att_date) > getdate(nowdate()):
			frappe.throw(_("Attendance can not be marked for future dates"))

	def validate_employee(self):
		emp = frappe.db.sql("select name from `tabEmployee` where name = %s and status = 'Active'",
		 	self.employee)
		if not emp:
			frappe.throw(_("Employee {0} is not active or does not exist").format(self.employee))

	def validate(self):
		# frappe.errprint("in validate")
		from erpnext.utilities import validate_status
		validate_status(self.status, ["Present", "Absent", "Half Day", "Pending approval", "Approved"])
		self.validate_fiscal_year()
		self.validate_att_date()
		self.validate_duplicate_record()
		self.check_leave_record()
		self.validate_time()
		self.validate_att_joining_date()
		self.validate_attendance_timing()

	def validate_attendance_timing(self):
		# frappe.errprint("in validate attendance timing")
		listt=[]
		time=''
		prev_time = None
		for d in self.get('attendance_time_sheet'):
			time=prev_time
			#frappe.errprint(time)
			if d.idx!=1:
				if time >= d.in_time:
					frappe.throw("for row '"+cstr(d.idx)+"' in time must be greater than the out time of its previous row ")
			prev_time = d.out_time
	
	def validate_att_joining_date(self):
		from datetime import datetime
		# frappe.errprint("in validate")
		if self.employee:
			date=frappe.db.sql("""select date_of_joining from `tabEmployee` where 
							name='%s'"""%self.employee,as_list=1)
			if date:
				d1 = datetime.strptime(date[0][0], "%Y-%m-%d")
				d2 = datetime.strptime(self.att_date, "%Y-%m-%d")
				if d1>d2:
					frappe.throw("You are trying to mark attendance for past days when employee is not joined")

	def validate_time(self):
		# frappe.errprint("in validate time")
		in_time=[]
		out_time=[]
		#frappe.errprint(type(self.get('attendance_time_sheet')))
		for d in self.get('attendance_time_sheet'):
			if d.in_time:
				# frappe.errprint(d.in_time)
				if d.in_time in in_time:
					frappe.throw("Duplicate In Time Entry")
				else:
					in_time.append(d.in_time)
			if d.out_time:
				if d.out_time in out_time:
					frappe.throw("Duplicate Out Time Entry")
				else:
					out_time.append(d.out_time)

		# frappe.errprint(in_time)
		# frappe.errprint(out_time)
		
	def validate_total_hours(self):
		#frappe.errprint(self.total_hours)
		if self.total_hours<=7.30:
			pass
		else:
			frappe.throw("Total Working hours for 1 day can not be greater than 7.30 hours")

	def on_update(self):
		# this is done because sometimes user entered wrong employee name
		# while uploading employee attendance
		employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
		frappe.db.set(self, 'employee_name', employee_name)
		#self.validate_total_break_hours()

	def validate_total_break_hours(self):
		import datetime as dt
		doc1 = frappe.get_doc("Attendance", self.name)
		#frappe.errprint(doc1)
		time = doc1.get('attendance_time_sheet')
		break_time1=0.0
		for i in range(0,len(time)):
			if i+1 < len(time):
				start_dt = dt.datetime.strptime(time[i].out_time, '%H:%M:%S')
				#frappe.errprint(start_dt)
				end_dt = dt.datetime.strptime(time[i+1].in_time, '%H:%M:%S')
				#frappe.errprint(end_dt)
				diff = (end_dt - start_dt)
				#frappe.errprint(diff)
				break_time=diff.seconds/60 
				#frappe.errprint(break_time)
				#break_time=break_time/60
				break_time1=break_time1+break_time
				#frappe.errprint(break_time1/60)
		#doc1.total_break_hours=break_time1
		#frappe.errprint(break_time1)
		frappe.db.set_value("Attendance", self.name, "total_break_hours", break_time1/60)

		#doc1.save(ignore_permissions=True)


	def get_hours(self,args):
		import datetime as dt
		try:
			start_dt = dt.datetime.strptime(args['in_time'], '%H:%M:%S')
			end_dt = dt.datetime.strptime(args['out_time'], '%H:%M:%S')
			diff = (end_dt - start_dt)
			return{
			"hours": diff.seconds/60
			}

		except Exception, e:
			frappe.msgprint("Enter Valid Time")