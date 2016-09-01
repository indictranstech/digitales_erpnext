// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
cur_frm.add_fetch('employee','attendance_approver','attendance_approver')

cur_frm.cscript.onload = function(doc, cdt, cdn) {
	if(doc.__islocal) cur_frm.set_value("att_date", get_today());
}

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{
		query: "erpnext.controllers.queries.employee_query"
	}	
}


cur_frm.cscript.in_time = function(doc,cdt,cdn){
	var d = locals[cdt][cdn];
	if(d.out_time){
		var args = {'in_time':d.in_time, 'out_time':d.out_time}
		get_server_fields('get_hours',JSON.stringify(args),'',doc, cdt, cdn, 1,function(r,rt){refresh_field('attendance_time_sheet')});
	}

}

cur_frm.cscript.out_time = function(doc,cdt,cdn){
	var d = locals[cdt][cdn];
	if(d.in_time){
		var args = {'in_time':d.in_time, 'out_time':d.out_time}
		get_server_fields('get_hours',JSON.stringify(args),'',doc, cdt, cdn, 1,function(r,rt){refresh_field('attendance_time_sheet')});
	}

}

cur_frm.cscript.validate = function(doc,cdt,cdn) {
	update_total_hour(doc);
	//cur_frm.cscript.update_total_break_time(doc);
}


update_total_hour = function(doc) {
	var td=0.0;
	var min = 0.0
	var el = doc.attendance_time_sheet;

	for(var i in el) {
		td += flt(el[i].hours,2);
	}
	var doc = locals[doc.doctype][doc.name];
	doc.total_hours = Math.floor(td/60);
	doc.minutes =  td%60;
	refresh_many(['total_hours','minutes']);
}

cur_frm.cscript.refresh=function(doc,cdt,cdn){
	unhide_field('attendance_time_sheet');
	unhide_field('total_hours');

}

cur_frm.cscript.status=function(doc,cdt,cdn){
	if(doc.status =='Present' || doc.status=='Half Day'){
		unhide_field('attendance_time_sheet');
		unhide_field('total_hours');
	}
	else{
		hide_field('attendance_time_sheet');
		hide_field('total_hours');
	}
}