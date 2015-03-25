// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

cur_frm.add_fetch('employee', 'hour_rate', 'hour_rate');

cur_frm.add_fetch('employee', 'department', 'department');

cur_frm.add_fetch('employee', 'branch', 'branch');

cur_frm.add_fetch('employee', 'designation', 'designation');

cur_frm.add_fetch('employee', 'bank_name', 'bank_name');

cur_frm.add_fetch('employee', 'bank_ac_no', 'bank_account_no');






cur_frm.cscript.from_date= function(doc, cdt, cdn) {
	//console.log("in from date")
	if (doc.from_date && doc.to_date)
	{
		var date1 = new Date(doc.from_date);
		var date2 = new Date(doc.to_date);
		var timeDiff = Math.abs(date2.getTime() - date1.getTime());
		var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
		//console.log("helllllllllllllllllllllllll11") 
		//console.log(diffDays)
		//doc.diff=doc.diffDays;
		//refresh_field('diff');
		if(date1>date2){
			msgprint("From Date must be less than To Date")
		}
		if(doc.employee){
			//if(diffDays == 14){
			//console.log("in from date date diff")
			//console.log(frappe.datetime.get_diff(doc.to_date, doc.from_date))
			var arg = {'month_start_date':doc.from_date, 'month_end_date':doc.to_date,'employee':doc.employee,'date_diff':diffDays}
			get_server_fields('get_weeklyofday_details',JSON.stringify(arg),doc.to_date,doc, cdt, cdn, 1 , function(r){
			refresh_field('total_days_in_month')	
			refresh_field('employee')
			});
			//}
			//else{
			//	msgprint("Dates diffrence is not equal to the two weeks")
			//}
		}
     
	}
};


cur_frm.cscript.to_date= function(doc, cdt, cdn) {
	//console.log("in the to date");
	if (doc.from_date && doc.to_date)
	{	
		var date1 = new Date(doc.from_date);
		var date2 = new Date(doc.to_date);
		var timeDiff = Math.abs(date2.getTime() - date1.getTime());
		var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
		//doc.diff=doc.diffDays
		//refresh_field('diff')
		//console.log("helllllllllllllllllllllllll22")
		//console.log(diffDays)
		if(date2<date1){
			msgprint("To Date must be greater than From Date")
		}
		if(doc.employee){
			//console.log(diffDays)
			//if(diffDays == 14){
			var arg = {'month_start_date':doc.from_date, 'month_end_date':doc.to_date,'employee':doc.employee,'date_diff':diffDays}
			get_server_fields('get_weeklyofday_details',JSON.stringify(arg),doc.to_date,doc, cdt, cdn, 1 , function(r){
				refresh_field('total_days_in_month');
				refresh_field('employee')
			});
			//}
			//else{
			//	msgprint("Dates diffrence is not equal to the two weeks")
			//}
		}
	}

};

cur_frm.cscript.employee= function(doc, cdt, cdn) {
	//console.log("in employee");
	var date1 = new Date(doc.from_date);
	var date2 = new Date(doc.to_date);
	var timeDiff = Math.abs(date2.getTime() - date1.getTime());
	var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
	//doc.diff=doc.diffDays
	//refresh_field('diff')
	if (doc.from_date && doc.to_date)
	{ 

		//console.log(diffDays)
		//alert("hiiii")
		//if(diffDays == 14){
		var arg = {'month_start_date':doc.from_date, 'month_end_date':doc.to_date,'employee':doc.employee,'date_diff':diffDays}
		//alert("hi");
		get_server_fields('get_weeklyofday_details',JSON.stringify(arg),doc.to_date,doc, cdt, cdn, 1 , function(r){
			//console.log(r.total_days_in_month)	
			refresh_field('total_days_in_month');
			refresh_field('employee')
		});
		//}
		//else{
		//	msgprint("Dates diffrence is not equal to the two weeks")
		//}
	}
};


cur_frm.cscript.fiscal_year = function(doc,dt,dn){
	    var date1 = new Date(doc.from_date);
		var date2 = new Date(doc.to_date);
		var timeDiff = Math.abs(date2.getTime() - date1.getTime());
		var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
		//doc.diff=doc.diffDays;
		//refresh_field('diff');
		if (doc.from_date && doc.to_date && doc.employee)
		{ 
			//if(diffDays == 14){
			return $c_obj(doc, 'get_emp_and_leave_details',diffDays,function(r, rt) {
			var doc = locals[dt][dn];
			cur_frm.refresh();
			calculate_all(doc, dt, dn);
			refresh_field(['total_days_in_month','payment_days','leave_without_pay','employee'])
			refresh_field(['earning_details','deduction_details'])
			
			});
			//}
			//else{
			//	msgprint("Dates diffrence is not equal to the two weeks")
			//}

		}
}

cur_frm.cscript.month = cur_frm.cscript.employee = cur_frm.cscript.fiscal_year;

cur_frm.cscript.leave_without_pay = function(doc,dt,dn){
	//console.log("leave_without_pay")
	if (doc.employee && doc.fiscal_year) {
		return $c_obj(doc, 'get_leave_details',doc.leave_without_pay,function(r, rt) {
			var doc = locals[dt][dn];
			cur_frm.refresh();
			calculate_all(doc, dt, dn);
		});
	}
 }

var calculate_all = function(doc, dt, dn) {
	//console.log("inc calculate_all")
	calculate_earning_total(doc, dt, dn);
	calculate_ded_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
}

cur_frm.cscript.e_modified_amount = function(doc,dt,dn){
	//calculate_earning_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
}

cur_frm.cscript.e_depends_on_lwp = cur_frm.cscript.e_modified_amount;

// Trigger on earning modified amount and depends on lwp
// ------------------------------------------------------------------------
cur_frm.cscript.d_modified_amount = function(doc,dt,dn){
	calculate_ded_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
}

cur_frm.cscript.d_depends_on_lwp = cur_frm.cscript.d_modified_amount;

// Calculate earning total
// ------------------------------------------------------------------------
var calculate_earning_total = function(doc, dt, dn) {
	//console.log("earning total")
	var tbl = doc.earning_details || [];

	var total_earn = 0;
	for(var i = 0; i < tbl.length; i++){
		//if(cint(tbl[i].e_depends_on_lwp) == 1) {
		tbl[i].e_modified_amount = Math.round(tbl[i].e_amount)*(flt(doc.payment_days)/cint(doc.total_days_in_month)*100)/100;			
		refresh_field('e_modified_amount', tbl[i].name, 'earning_details');
		//}
		total_earn += flt(tbl[i].e_modified_amount);
	}
	doc.gross_pay = total_earn + flt(doc.arrear_amount) + flt(doc.leave_encashment_amount);
	refresh_many(['e_modified_amount', 'gross_pay']);
}

// Calculate deduction total
// ------------------------------------------------------------------------
var calculate_ded_total = function(doc, dt, dn) {
	var tbl = doc.deduction_details || [];

	var total_ded = 0;
	for(var i = 0; i < tbl.length; i++){
		//if(cint(tbl[i].d_depends_on_lwp) == 1) {
		tbl[i].d_modified_amount = Math.round(tbl[i].d_amount)*(flt(doc.payment_days)/cint(doc.total_days_in_month)*100)/100;
		refresh_field('d_modified_amount', tbl[i].name, 'deduction_details');
		//}
		total_ded += flt(tbl[i].d_modified_amount);
	}
	doc.total_deduction = total_ded;
	refresh_field('total_deduction');	
}

// Calculate net payable amount
// ------------------------------------------------------------------------
var calculate_net_pay = function(doc, dt, dn) {
	doc.net_pay = flt(doc.gross_pay) - flt(doc.total_deduction);
	doc.rounded_total = Math.round(doc.net_pay);
	refresh_many(['net_pay', 'rounded_total']);
}

// trigger on arrear
// ------------------------------------------------------------------------
cur_frm.cscript.arrear_amount = function(doc,dt,dn){
	calculate_earning_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
}

// trigger on encashed amount
// ------------------------------------------------------------------------
cur_frm.cscript.leave_encashment_amount = cur_frm.cscript.arrear_amount;

// validate
// ------------------------------------------------------------------------
cur_frm.cscript.validate = function(doc, dt, dn) {
	calculate_all(doc, dt, dn);
}

// // cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
// // 	return{
// // 		query: "erpnext.controllers.queries.employee_query"
// // 	}		
// // }
