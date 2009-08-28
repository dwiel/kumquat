var triple_value_uri_name = '';

function delete_triple(sub, pred, obj, row) {
	$.post("/action/delete_triple", {
		'sub' : sub, 
		'pred' : pred,
		'obj' : obj}, function (data) {
			$('#row'+row).hide();
		}
	);
}

function parse_prim(prim) {
	t = prim.substr(0,1);
	if(t == 's') {
		return prim.substr(1);
	} else if(t == 'n') {
		return prim.substr(1);
	} else if(t == 'i') {
		return prim.substr(1);
	} else if(t == 'u') {
// 		return '<%s>' % re_uri.sub('', prim.substr(1))
		return prim.substr(1);
	} else if(t == 'a') {
		return prim.substr(1);
// 		name = schema.name_to_uri(prim.substr(1))
// 		if(name)
// 			return '<%s>' % name
// 		else
// 			return None
	} else {
		return "unknown data type";
	}
}

function insert_triple(sub, pred, obj) {
	$.post("/action/insert_triple", {
		'sub' : sub, 
		'pred' : pred,
		'obj' : obj}, function (data) {
			//done
		}
	);
	
	row = parseInt($('#row_count').html()) + 1;
	
	$('#new_triple').hide();
	ppred = parse_prim(pred);
	disp_obj = get_triple_value_display();
	row = '<tr id="row'+row+'"><td><a href="javascript:delete_triple(\'u' + $('#advanced').html() + '\',\'' + pred + '\',\'' + obj + '\',' + row + ');">x</a> <a href="/view/name/' + ppred + '">' + parse_prim(pred) + '</a></td><td>' + disp_obj + '</td></tr>';
	$('#triplestable table').html( $('#triplestable table').html() + row );

}

function show_add_triple() {
	$('#new_triple').show();
}
function toggle_uri() {
	$('#uri').toggle();
}
function formatItem(item) {
	return item[0];
}
function value_onItemSelect(li) {
	if($(li).html() != '') {
		$('#new_triple_submit').show();
		$('#triple_value_uri').val(li.extra[0]);
		triple_value_uri_name = $(li).html();
//		TODO: make this work again, preferably with insert triple
// 		value = li.extra[0];
// 		insert_triple('a'+$('#subject_name').html(), 'a'+$('#new_triple_property').val(), 'u'+value);
	}
}
function property_onItemSelect(li) {
	if($(li).html() != '') {
		input_type = li.extra[0];
		if(input_type == 'suggest') {
			$('#new_triple_value').autocomplete("/api/existing_values_autocomplete", {
				extraParams: {
					property_name: $(li).html()
				},
				mustMatch: true,
				onItemSelect: value_onItemSelect,
				minChars:0,
			})
			$('#new_triple_value').show();
			get_triple_value = function() {
				return 'u'+$('#triple_value_uri').val();
			};
			get_triple_value_display = function() {
				return '<a href="/view/name/' + triple_value_uri_name + '">' +  triple_value_uri_name + '</a>';
			}
		} else {
			$('#new_triple_submit').show();
			if(input_type == 'textarea') {
				$('#new_triple_value_textarea').show();
				get_triple_value = function() {
					return 's'+$('#new_triple_value_textarea').val();
				}
				get_triple_value_display = function() {
					return $('#new_triple_value_textarea').val();
				}
			} else if(input_type == 'plain') {
				$('#new_triple_value').show();
				get_triple_value = function() {
					return 's'+$('#new_triple_value').val();
				}
				get_triple_value_display = function() {
					return $('#new_triple_value').val();
				}
			} else if(input_type == 'integer') {
				$('#new_triple_value').show();
				get_triple_value = function() {
					return 'i'+$('#new_triple_value').val();
				}
				get_triple_value_display = function() {
					return $('#new_triple_value').val();
				}
			}
		}
	}
}

$(document).ready(function() {
	$('#new_triple_value_textarea').hide();
	$('#new_triple_submit').hide();
	$('#uri').hide();
	$('#subject_name').hide();
	$('#new_triple').hide();
	$('#new_triple_value').hide();
	$('#new_triple_submit').click(function() {
		insert_triple('a'+$('#subject_name').html(), 'a'+$('#new_triple_property').val(), get_triple_value());
	});
	$('#new_triple_property').autocomplete("/api/types_properties_autocomplete", {
		extraParams: {
			types: $('#types').attr('value')
		},
		mustMatch: true,
		onItemSelect : property_onItemSelect,
		onItemLost : function() {
			$('#new_triple_value').hide();
		},
		formatItem:formatItem,
		matchContains:true,
		matchSubset:true,
		cacheLength:10,
		selectFirst:true,
		minChars:0,
	});
});