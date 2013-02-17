$(document).ready(function() {
	
	function pyStringToList(a) {
		a = a.replace('[', '');
		a = a.replace(']', '');
		a = a.replace(',', '');
		a = a.split(' ');
		ret = [];
		for(var i = 0; i<a.length; i++) {
			ret.push(parseInt(a[i]));
		}
		// console.log("ret:" + ret.toString());
		return ret;
	}
	var JAVA_STR = 'Java';
	var PYTHON_STR = 'Python';

	var modes = {};
	modes[JAVA_STR] = 'text/x-java';
	modes[PYTHON_STR] = 'text/x-python';

	var sourceDict = {};
	sourceDict[JAVA_STR] = $('span#javaSource').text();
	sourceDict[PYTHON_STR] = $('span#pythonSource').text();
	var currLanguage = JAVA_STR;

	$('div#javaInfo').hide();
	$('div#pythonInfo').hide();

	// Set the inital text
	$('textarea#editor').text(sourceDict[currLanguage]);

	var codeMirror = CodeMirror.fromTextArea(document.getElementById("editor"),
		{
			mode : modes[JAVA_STR],
			collapseRange : true,
			lineNumbers : true,
			tabSize : 4,
			indentUnit: 4,
			indentWithTabs : true
		}
	);

	document.getElementById("languageSelector").onchange = function(event) {
		newLanguage = $('#languageSelector').val();
		var newMode = modes[newLanguage];
		var newSource = sourceDict[newLanguage];

		// Save the current source and set the new language
		sourceDict[currLanguage] = codeMirror.getValue();
		currLanguage = newLanguage;

		console.log("Changing source and mode to: " + newMode);
		codeMirror.setOption("mode", newMode);
		codeMirror.setOption("value", newSource);
	};

	$('input#submit').click(function(event) {
		event.preventDefault();
		event.stopPropagation();
		var csrftoken = $.cookie('csrftoken');
		var req = new XMLHttpRequest();

		req.onreadystatechange = function (oEvent) {
			if (req.readyState === 4)
			{
				console.log("Status: " + req.status);
				if (req.status === 200)
				{
					console.log("Response: " + req.responseText);
					$('div#result').text(req.responseText)
				}
				else
				{
					console.log("Error", req.statusText);
					console.log("Response: " + req.responseText);
				}
			}
		};

		req.open("POST", "/prog/problems/judge/" + problemName, true);
		req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
		req.setRequestHeader('X-CSRFToken', csrftoken);

		language = $('select#languageSelector').val();
		language = encodeURIComponent(language);

		source = codeMirror.getValue();
		source = encodeURIComponent(source);

		req.send("language=" + language + "&editor=" + source);

		$('div#result').text('Submitted. Waiting for response...');
	});
});