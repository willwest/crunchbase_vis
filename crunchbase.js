// Developer: William West
// Description: Functions for creating a Crunchbase organizations
//              visualization using D3 and JSON

// Create the donut chart using D3
var top_level = function(){
	var width = 300;
	var height = 300;
	var radius = Math.min(width,height)/2;

	var color = d3.scale.category10();

	var arc = d3.svg.arc()
					.outerRadius(radius - 10)
					.innerRadius(radius - 50);

	var pie = d3.layout.pie()
				.sort(null)
				.value(function(d) {
					return d.count;
				});

	var svg = d3.select("body")
				.append("svg")
				.attr("width", width)
				.attr("height", height)
				.append("g")
				.attr("transform", "translate(" + width / 2 + ',' +
					height / 2 + ')');

	d3.json("data/categories.json", function(error, graph){
		data = graph.categories;

		var g = svg.selectAll("arc")
				.data(pie(data))
				.enter().append("g")
				.attr("class", "arc cat")
				.attr('id', function (d) {
					return d.data.cat_name;
				})
				.on("mouseover", function() {
					d3.selectAll('.category_list').style('display', 'none');
					d3.select('.category_list#'+this.id).style('display', 'block');
				});
		g.append("path")
		.attr("d", arc)
		.style("fill", function (d) {
			return color(d.data.cat_id);
		});
	});
};

// Create the ul elements for each of the top 10 categories.
var make_lists = function(){
	$.getJSON('data/categories.json').done(function(data){
		for(var i=0; i<data.categories.length; i++){
			var cat_name = data.categories[i].cat_name;

			var title = document.createElement('h3');
			title.appendChild(document.createTextNode(cat_name));
			var entry = document.createElement('div');
			entry.setAttribute('id', cat_name);
			entry.setAttribute('class', "category_list");

			var list_container = document.getElementById('list_container');
			list_container.appendChild(entry);
			entry.appendChild(title);

			entry.appendChild(document.createElement('ul'));
		}
	});
};

// Create the individual li elements for each category
var print_organizations = function(){
	$.getJSON('data/org_cat.json', function(data){

		for(var i=0; i<data.nodes.length; i++){
			var cat_name = data.nodes[i].cat_name;
			var org_name = data.nodes[i].org_name;
			var org_link = data.nodes[i].org_link;

			var list_container = document.getElementById(cat_name);
			var list = list_container.getElementsByTagName('ul')[0];

			// Create the link element and add the appropriate attributes.
			var entry = document.createElement('li');
			var link = document.createElement('a');
			link.appendChild(document.createTextNode(org_name));
			link.setAttribute('href', org_link);
			link.setAttribute('target', '_blank');
			entry.appendChild(link);

			list.appendChild(entry);
		}
	});
};