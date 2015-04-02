// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

var display_activity_log = function(msg) {
	if(!pscript.ss_html)
		pscript.ss_html = $a(cur_frm.fields_dict['activity_log'].wrapper,'div');
	pscript.ss_html.innerHTML =
		'<div class="panel"><div class="panel-heading">'+__("Activity Log:")+'</div>'+msg+'</div>';
}

//Create salary slip
//-----------------------
cur_frm.cscript.create_salary_slip = function(doc, cdt, cdn) {
	var callback = function(r, rt){
		if (r.message)
			display_activity_log(r.message);
	}
	return $c('runserverobj', args={'method':'create_sal_slip','docs':doc},callback);
}

cur_frm.cscript.submit_salary_slip = function(doc, cdt, cdn) {
	var check = confirm(__("Do you really want to Submit all Salary Slip for the dates from date {0} and to date {1} and year {2}", [doc.from_date,doc.to_date, doc.fiscal_year]));
	if(check){
		var callback = function(r, rt){
			if (r.message)
				display_activity_log(r.message);
		}
		return $c('runserverobj', args={'method':'submit_salary_slip','docs':doc},callback);
	}
}

cur_frm.cscript.make_bank_voucher = function(doc,cdt,cdn){
    if(doc.company && doc.from_date && doc.to_date && doc.fiscal_year){
    	cur_frm.cscript.make_jv(doc, cdt, cdn);
    } else {
  	  msgprint(__("Company,From Date,To Date and Fiscal Year is mandatory"));
    }
}

cur_frm.cscript.make_jv = function(doc, dt, dn) {
	var call_back = function(r, rt){
		var jv = frappe.model.make_new_doc_and_get_name('Journal Voucher');
		jv = locals['Journal Voucher'][jv];
		jv.voucher_type = 'Bank Voucher';
		jv.user_remark = __('Payment of salary for the date from date {0} and to date {1} and year {2}', [doc.from_date,doc.to_date, doc.fiscal_year]);
		jv.fiscal_year = doc.fiscal_year;
		jv.company = doc.company;
		jv.posting_date = dateutil.obj_to_str(new Date());

		// credit to bank
		var d1 = frappe.model.add_child(jv, 'Journal Voucher Detail', 'entries');
		d1.account = r.message['default_bank_account'];
		d1.credit = r.message['amount']

		// debit to salary account
		var d2 = frappe.model.add_child(jv, 'Journal Voucher Detail', 'entries');
		d2.debit = r.message['amount']

		loaddoc('Journal Voucher', jv.name);
	}
	return $c_obj(doc, 'get_acc_details', '', call_back);
}



cur_frm.cscript.from_date= function(doc, cdt, cdn) {
	if (doc.from_date && doc.to_date)
	{
		var date1 = new Date(doc.from_date);
		var date2 = new Date(doc.to_date);
		var timeDiff = Math.abs(date2.getTime() - date1.getTime());
		var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
		//console.log(diffDays)
		if(date1>date2){
			msgprint("From Date must be less than To Date")
		}
		// if(diffDays != 14){
		// 	msgprint("Dates diffrence is not equal to the two weeks")
		// }
     
	}
};


cur_frm.cscript.to_date= function(doc, cdt, cdn) {
	if (doc.from_date && doc.to_date)
	{	
		var date1 = new Date(doc.from_date);
		var date2 = new Date(doc.to_date);
		var timeDiff = Math.abs(date2.getTime() - date1.getTime());
		var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
		//console.log(diffDays)
		if(date2<date1){
			msgprint("To Date must be greater than From Date")
		}
		if (doc.digitales_salary_structure=='Yes' && diffDays!=14){
			msgprint("If digitales salary structure is Yes then date diffrence between from date & to date must be equal to 14")
			doc.to_date=''
		}
		// doc.digitales_salary_structure = ''
		// //doc.to_date = ''
		// refresh_field('digitales_salary_structure');
		refresh_field('to_date');
		// if(diffDays != 14){
		// 	msgprint("Dates diffrence is not equal to the two weeks")
		// }
	}

};

cur_frm.cscript.digitales_salary_structure= function(doc,cdt,cdn){
	if(doc.from_date && doc.to_date)
	{	
		if (doc.digitales_salary_structure == 'Yes'){

			var date1 = new Date(doc.from_date);
			var date2 = new Date(doc.to_date);
			var timeDiff = Math.abs(date2.getTime() - date1.getTime());
			var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 
			if (diffDays!=14){
				msgprint("If digitales salary structure is Yes then date diffrence between from date & to date must be equal to 14")
				doc.to_date=''
			}
			
			refresh_field('to_date');
		}
	}
	else{
		msgprint("From Date and To Date can not be blanked")
	}

}