// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


cur_frm.cscript.start_date= function(doc, cdt, cdn) {
	//console.log("hii")
	if(doc.start_date){
		get_server_fields('check_start_date',doc.start_date,'',doc, cdt, cdn,1)

	}
}

cur_frm.cscript.end_date= function(doc, cdt, cdn) {
	//console.log("hii")
	if(doc.end_date && doc.start_date){
		get_server_fields('check_end_date',doc.end_date,'',doc, cdt, cdn,1)

	}
	else{
		msgprint("Please specify start date first");
	}
}