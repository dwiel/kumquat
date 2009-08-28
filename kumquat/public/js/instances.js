function add_column() {
	var column_name = '<input type="text" id="new-column-property" />';
	$('#instances tr:first').append('<th>' + column_name + '</th>');
	$('#instances tr:not(:first)').append('<td></td>');

	$('#new-column-property').autocomplete("/api/types_properties_autocomplete", {
		extraParams: {
			types: $('#types').attr('value')
		},
		mustMatch: true,
/*		onItemSelect : property_onItemSelect,
		onItemLost : function() {
			$('#new_triple_value').hide();
		},*/
// 		formatItem:formatItem,
		matchContains:true,
		matchSubset:true,
		cacheLength:10,
		selectFirst:true,
		minChars:0,
	});
}

$(document).ready(function() {
	$('#types').hide();
});