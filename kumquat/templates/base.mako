<%def name="sidebar()">
<%include file="sidebar.mako" />
</%def>

<%def name="triplestable()">
<%include file="triplestable.mako" />
</%def>

<html>
<head>
    <script src="/js/jquery-1.3.2.min.js" type="text/javascript"></script>
		% for js in c.jsincludes:
			<script src="/js/${js}" type="text/javascript"></script>
		% endfor
		<link rel="stylesheet" href="/css/blueprint/screen.css" type="text/css" media="screen, projection" />
    <link rel="stylesheet" href="/css/blueprint/print.css" type="text/css" media="print" /> 
    <!--[if IE]>
        <link rel="stylesheet" href="/css/blueprint/ie.css" type="text/css" media="screen, projection" />
    <![endif]-->
    <link rel="stylesheet" HREF="/css/style.css" type="text/css" />
		% for css in c.cssincludes:
			<link rel="stylesheet" HREF="/css/${css}" type="text/css" />
		% endfor
		<title>
        ${self.title()}
    </title>
</head>
<body>
    <div class="container">
        <div id="sidebar" class="span-4">
            <div id="site_name" class="em">
                <hr \>
								<a id="logo" href="/">
										<div id="logo_the">The</div><div id="logo_burning">Burning</div><div id="logo_kumquat">Kumquat</div>
								</a>
                <hr \>
            </div>
			<div id="menu">
            ${self.sidebar()}
			</div>
        </div>
        <div id="content" class="span-19 last colborderleft">
            ${self.body()}
        </div>
		${self.triplestable()}
		% if c.post_body :
			<br>
			<br>
			<hr>
			${c.post_body}
		% endif
    </div>
</body>
</html>