# Dev: William West
# Description: Crawls the Crunchbase API and dumps/processes a dataset of
#              organization information.

import urllib3
import json
import time
import sys

API_KEY = "YOUR API KEY HERE"

# Given a url, make a GET request with exponential backoff
def make_request(url):
	http = urllib3.PoolManager()

	backoff = 5
	while True:	
		try:
			r = http.request('GET', url, timeout=urllib3.Timeout(total=5.0))
			if r.status != 200:
				raise IOError("Error: couldn't crawl " + url)
			return r.data
		except urllib3.exceptions.TimeoutError:
			print "Error: timed out on url: " + url
			print "Sleeping for " + str(backoff) + " seconds..."

		# exponential backoff
		backoff = 2 ** backoff

def get_organization(path):
	print "Crawling {}".format(path)

	url = ("http://api.crunchbase.com/v/2/{}?"
		   "user_key={}").format(path, API_KEY)

	try:
		data = json.loads(make_request(url))
	except IOError:
		raise IOError("Could not crawl organization: {}".format(path))

	return data


def update_organizations(order="DESC", sorting="created_at"):
	'''Update our raw dataset with newly added organizations'''
	with open('data/organizations.json', 'r') as f:
		current_organizations = json.load(f)

	page = 1
	url = ("http://api.crunchbase.com/v/2/organizations?"
		  "user_key={}&page={}&order={}+{}").format(API_KEY, page, sorting, order)

	data = json.loads(make_request(url))

	metadata = data["metadata"]
	paging = data["data"]["paging"]
	new_items = data["data"]["items"]

	# Get paths for current organizations
	current_organization_paths = [n["path"] for n in current_organizations]

	# If we found any new organizations in this request, crawl their details
	# and then add it to our dataset.
	for new_item in new_items:
		if new_item["path"] not in current_organization_paths:
			try:
				new_item["extended"] = get_organization(new_item["path"])
				current_organizations.append(new_item)
			except IOError:
				print ("Error: Couldn't crawl {}."
					   "Removing...").format(new_item["path"])
				continue

	with open('data/organizations.json', 'w') as outfile:
		json.dump(current_organizations, outfile)

def has_category(org):
	if "relationships" not in org["extended"]["data"]:
		return False
	if "categories" in org["extended"]["data"]["relationships"]:
		return True
	else:
		return False

def generate_production_data():
	'''Create the final dataset for use in production web application. The 
	data will consist of a set of nodes containing each organization's name
	and category.'''
	category_types = set()
	category_counts = {}
	top_categories = []
	nodes = []

	with open('data/organizations.json', 'r') as f:
		organizations = json.load(f)

	for org in organizations:
		if has_category(org):
			extended_data = org["extended"]["data"]
			categories = extended_data["relationships"]["categories"]["items"]
			for category in categories:
				cat_name = category["name"]
				nodes.append({"org_name":org["name"],"org_link":"http://www.crunchbase.com/"+org["path"], "category":cat_name})
				category_types.add(cat_name)
				if cat_name in category_counts:
					category_counts[cat_name] += 1
				else:
					category_counts[cat_name] = 1

	# Get sorted list of top 10 category counts
	for cat in sorted(category_counts, key=category_counts.get, reverse=True):
		top_categories.append(cat)
	top_categories = top_categories[:10]

	category_types = list(category_types)

	# Remove all nodes not in top categories
	for node in nodes[:]:
		if node["category"] in top_categories:
			node["cat_name"] = node["category"].replace(' ','_')
			node["category"] = top_categories.index(node["category"])+1
		else:
			nodes.remove(node)

	with open('data/org_cat.json', 'w') as f:
		json.dump({"nodes":nodes}, f)

	with open('data/categories.json', 'w') as f:
		final_cats = []
		for category in top_categories:
			final_cats.append({"cat_name":category.replace(' ','_'), "cat_id":top_categories.index(category)+1, "count":category_counts[category]})

		json.dump({"categories":final_cats}, f)

# Execute once per hour
while True:
	sys.stdout.write( "Updating...")
	update_organizations()
	sys.stdout.write("done.\n")
	sys.stdout.write("Generating production data...")
	generate_production_data()
	sys.stdout.write("done.\n")

	sys.stdout.write("Sleeping for 60 minutes...")
	# Sleep for 1 hour
	time.sleep(3600)
	sys.stdout.write("done.\n")

