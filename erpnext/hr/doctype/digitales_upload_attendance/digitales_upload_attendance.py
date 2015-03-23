# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.utils import cstr,cint, add_days, date_diff
from frappe import _
from frappe.utils.csvutils import UnicodeWriter
from frappe.model.document import Document

class DigitalesUploadAttendance(Document):
	pass


@frappe.whitelist()
def get_template():
	if not frappe.has_permission("Attendance", "create"):
		raise frappe.PermissionError

	args = frappe.local.form_dict

	w = UnicodeWriter()
	w = add_header(w)

	w = add_data(w, args)

	# write out response as a type csv
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Attendance"

def add_header(w):
	status = ", ".join((frappe.get_meta("Attendance").get_field("status").options or "").strip().split("\n"))
	w.writerow(["Notes:"])
	w.writerow(["Please do not change the template headings"])
	w.writerow(["Status should be one of these values: " + status])
	w.writerow(["If you are overwriting existing attendance records, 'ID' column mandatory"])
	w.writerow(["DocType:", "Attendance", "", "", "",
	 	"", "", "","~","Attendance Time Sheets","attendance_time_sheet"])
	w.writerow(["ID", "Employee", "Employee Name", "Date", "Status",
		"Fiscal Year", "Company", "Naming Series","~","ID","In Time","Out Time"])
	return w

def add_data(w, args):
	from erpnext.accounts.utils import get_fiscal_year

	dates = get_dates(args)
	employees = get_active_employees()
	existing_attendance_records = get_existing_attendance_records(args)
	for date in dates:
		frappe.errprint(date)
		for employee in employees:
			existing_attendance = {}
			if existing_attendance_records \
				and tuple([date, employee.name]) in existing_attendance_records:
					existing_attendance = existing_attendance_records[tuple([date, employee.name])]
			row = [
				existing_attendance and existing_attendance.name or "",
				employee.name, employee.employee_name, date,
				existing_attendance and existing_attendance.status or "",
				get_fiscal_year(date)[0], employee.company,
				existing_attendance and existing_attendance.naming_series or get_naming_series(),
			]
			w.writerow(row)
			w.writerow("\n")
	return w

def get_dates(args):
	"""get list of dates in between from date and to date"""
	no_of_days = date_diff(add_days(args["to_date"], 1), args["from_date"])
	dates = [add_days(args["from_date"], i) for i in range(0, no_of_days)]
	return dates

def get_active_employees():
	employees = frappe.db.sql("""select name, employee_name, company
		from tabEmployee where docstatus < 2 and status = 'Active'""", as_dict=1)
	return employees

def get_existing_attendance_records(args):
	attendance = frappe.db.sql("""select name, att_date, employee, status, naming_series
		from `tabAttendance` where att_date between %s and %s and docstatus < 2""",
		(args["from_date"], args["to_date"]), as_dict=1)

	existing_attendance = {}
	for att in attendance:
		existing_attendance[tuple([att.att_date, att.employee])] = att

	return existing_attendance

def get_naming_series():
	series = frappe.get_meta("Attendance").get_field("naming_series").options.strip().split("\n")
	if not series:
		frappe.throw(_("Please setup numbering series for Attendance via Setup > Numbering Series"))
	return series[0]


@frappe.whitelist()
def upload():
	if not frappe.has_permission("Attendance", "create"):
		raise frappe.PermissionError

	from frappe.utils.csvutils import read_csv_content_from_uploaded_file
	from frappe.modules import scrub

	rows = read_csv_content_from_uploaded_file()
	rows = filter(lambda x: x and any(x), rows)
	#frappe.errprint(rows)
	if not rows:
		msg = [_("Please select a csv file")]
		return {"messages": msg, "error": msg}
	columns = [scrub(f) for f in rows[5]]
	#frappe.errprint(columns)
	columns[0] = "name"
	columns[3] = "att_date"
	#frappe.errprint(columns)
	ret = []
	error = False

	from frappe.utils.csvutils import check_record
	dict1={}
	att_id=''
	worked_hours=''
	for i, row in enumerate(rows[6:]):
		#frappe.errprint(i)
		#frappe.errprint(row)
		
		if row[1] and row[3]:
			dict1={'employee':row[1],'att_date':row[3],'status':row[4],'fiscal_year':row[5],'company':row[6],'naming_series':row[7],'employee_name':row[2]}
			
		dict1['in_time'] = row[10]
		dict1['out_time']=row[11]

		if not row: continue
		row_idx = i + 6
		#d = frappe._dict(zip(columns, row))
		
		dict1["doctype"] = "Attendance"
		if dict1.get('name'):
			dict1["docstatus"] = frappe.db.get_value("Attendance", dict1.get('name'), "docstatus")

		try:
			check_record(dict1)
			if row[1] and row[3]:
				att_id=import_doc(dict1, "Attendance", 1, row_idx, submit=True)
				make_child_entry(att_id,dict1,worked_hours)
				ret.append('Inserted row (#%d) %s' % (row_idx + 1, getlink('Attendance',
			att_id)))
			else:
				#frappe.errprint([worked_hours])
				make_child_entry(att_id,dict1,worked_hours)

			#frappe.errprint(d.name)
		except Exception, e:
			error = True
			ret.append('Error for row (#%d) %s : %s' % (row_idx,
				len(row)>1 and row[1] or "", cstr(e)))
			frappe.errprint(frappe.get_traceback())

	if error:
		frappe.db.rollback()
	else:
		frappe.db.commit()

	return {"messages": ret, "error": error,"name":dict1.get('name')}

def import_doc(d, doctype, overwrite, row_idx, submit=False, ignore_links=False):
	#frappe.errprint("in import doc")
	"""import main (non child) document"""
	if d.get("name") and frappe.db.exists(doctype, d['name']):
		if overwrite:
			doc = frappe.get_doc(doctype, d['name'])
			doc.ignore_links = ignore_links
			doc.update(d)
			if d.get("docstatus") == 1:
				doc.update_after_submit()
			else:
				doc.save()
			return 'Updated row (#%d) %s' % (row_idx + 1, getlink(doctype, d['name']))
		else:
			return 'Ignored row (#%d) %s (exists)' % (row_idx + 1,
				getlink(doctype, d['name']))
	else:
		doc = frappe.get_doc(d)
		doc.ignore_links = ignore_links
		doc.insert()

		if submit:
			doc.submit()

		return doc.get('name')


def getlink(doctype, name):
	return '<a href="#Form/%(doctype)s/%(name)s">%(name)s</a>' % locals()

def make_child_entry(att_id,dict1,worked_hours):
	import datetime as dt
	start_dt = dt.datetime.strptime(dict1.get('in_time'), '%H:%M:%S')
	end_dt = dt.datetime.strptime(dict1.get('out_time'), '%H:%M:%S')
	diff = (end_dt - start_dt) 
	att=frappe.new_doc("Attendance Time Sheets")
	att.in_time=dict1.get('in_time')
	att.out_time=dict1.get('out_time')
	att.parent=att_id
	att.parentfield='attendance_time_sheet'
	att.parenttype='Attendance'
	att.hours=diff.seconds/60
	att.docstatus=1
	att.save(ignore_permissions=True)
	worked_hours=cint(worked_hours) + cint(diff.seconds/60)
	#frappe.errprint(worked_hours)
	prt = frappe.get_doc('Attendance', att_id)
	total_hours=((cint(prt.total_hours)*60)+cint(worked_hours))/60
	frappe.db.sql("""update `tabAttendance` set total_hours='%s' where name='%s'"""%(total_hours,att_id))
	frappe.db.commit()
