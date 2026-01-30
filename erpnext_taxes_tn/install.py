"""
Installation script for erpnext_taxes_tn app
=============================================

Creates Tax Accounts, Tax Templates, and Tax Categories for Tunisian companies.
"""

import frappe
from frappe import _


def after_install():
	"""
	Called after app installation.
	Sets up Tunisian tax configuration for all Tunisian companies.
	"""
	setup_tunisia_taxes()


def setup_tunisia_taxes():
	"""
	Main setup function to create all Tunisian tax configuration.
	"""
	print("Setting up Tunisian TVA configuration...")

	# Create Tax Category
	create_tax_category()

	# Get all Tunisian companies
	companies = frappe.get_all(
		"Company",
		filters={"country": "Tunisia"},
		fields=["name", "abbr"]
	)

	if not companies:
		print("[WARNING]","No Tunisian companies found. Skipping tax setup.")
		return

	for company in companies:
		setup_company_taxes(company.name, company.abbr)

	frappe.db.commit()
	print("Tunisian TVA configuration completed!")


def create_tax_category():
	"""Create Tax Category 'Tunisia' if it doesn't exist."""
	if not frappe.db.exists("Tax Category", "Tunisia"):
		doc = frappe.get_doc({
			"doctype": "Tax Category",
			"name": "Tunisia",
			"title": "Tunisia"
		})
		doc.insert(ignore_permissions=True)
		print("Created Tax Category: Tunisia")


def setup_company_taxes(company, abbr):
	"""
	Set up tax accounts and templates for a specific company.

	Args:
		company: Company name
		abbr: Company abbreviation
	"""
	print(f"Setting up taxes for company: {company}")

	# Define Tunisian tax rates
	tax_rates = [
		{"rate": 19, "name": "TVA 19% - TN", "description": "Standard rate"},
		{"rate": 13, "name": "TVA 13% - TN", "description": "Reduced rate"},
		{"rate": 7, "name": "TVA 7% - TN", "description": "Super-reduced rate"},
		{"rate": 0, "name": "TVA 0% - TN", "description": "Zero rate (Export)"},
	]

	# Get or create parent account (Duties and Taxes)
	parent_account = get_duties_and_taxes_account(company, abbr)

	if not parent_account:
		print("[WARNING]",f"Could not find Duties and Taxes account for {company}")
		return

	# Create tax accounts
	for tax in tax_rates:
		create_tax_account(
			account_name=tax["name"],
			parent_account=parent_account,
			company=company,
			abbr=abbr
		)

	# Create tax templates
	create_sales_templates(company, abbr)
	create_purchase_templates(company, abbr)


def get_duties_and_taxes_account(company, abbr):
	"""Get the Duties and Taxes parent account for the company."""
	account_name = f"Duties and Taxes - {abbr}"

	if frappe.db.exists("Account", account_name):
		return account_name

	# Try to find it by account_name
	account = frappe.db.get_value(
		"Account",
		{"account_name": "Duties and Taxes", "company": company},
		"name"
	)

	return account


def create_tax_account(account_name, parent_account, company, abbr):
	"""
	Create a tax account if it doesn't exist.

	Args:
		account_name: Name without company abbreviation (e.g., "TVA 19% - TN")
		parent_account: Parent account name
		company: Company name
		abbr: Company abbreviation
	"""
	full_name = f"{account_name} - {abbr}"

	if frappe.db.exists("Account", full_name):
		return full_name

	doc = frappe.get_doc({
		"doctype": "Account",
		"account_name": account_name,
		"parent_account": parent_account,
		"company": company,
		"account_type": "Tax",
		"is_group": 0
	})
	doc.insert(ignore_permissions=True)
	print(f"Created account: {full_name}")

	return full_name


def create_sales_templates(company, abbr):
	"""Create Sales Taxes and Charges Templates for the company."""
	templates = [
		{
			"title": "Tunisia - Sales TVA 19%",
			"rate": 19.0,
			"account": f"TVA 19% - TN - {abbr}",
			"description": "TVA 19%"
		},
		{
			"title": "Tunisia - Sales TVA 13%",
			"rate": 13.0,
			"account": f"TVA 13% - TN - {abbr}",
			"description": "TVA 13%"
		},
		{
			"title": "Tunisia - Sales TVA 7%",
			"rate": 7.0,
			"account": f"TVA 7% - TN - {abbr}",
			"description": "TVA 7%"
		},
		{
			"title": "Tunisia - Export TVA 0%",
			"rate": 0.0,
			"account": f"TVA 0% - TN - {abbr}",
			"description": "TVA 0% (Export)"
		},
	]

	for tmpl in templates:
		create_tax_template(
			doctype="Sales Taxes and Charges Template",
			title=tmpl["title"],
			company=company,
			rate=tmpl["rate"],
			account=tmpl["account"],
			description=tmpl["description"]
		)


def create_purchase_templates(company, abbr):
	"""Create Purchase Taxes and Charges Templates for the company."""
	templates = [
		{
			"title": "Tunisia - Purchase TVA 19%",
			"rate": 19.0,
			"account": f"TVA 19% - TN - {abbr}",
			"description": "TVA 19%"
		},
		{
			"title": "Tunisia - Purchase TVA 13%",
			"rate": 13.0,
			"account": f"TVA 13% - TN - {abbr}",
			"description": "TVA 13%"
		},
		{
			"title": "Tunisia - Purchase TVA 7%",
			"rate": 7.0,
			"account": f"TVA 7% - TN - {abbr}",
			"description": "TVA 7%"
		},
	]

	for tmpl in templates:
		create_tax_template(
			doctype="Purchase Taxes and Charges Template",
			title=tmpl["title"],
			company=company,
			rate=tmpl["rate"],
			account=tmpl["account"],
			description=tmpl["description"]
		)


def create_tax_template(doctype, title, company, rate, account, description):
	"""
	Create a tax template if it doesn't exist.

	Args:
		doctype: "Sales Taxes and Charges Template" or "Purchase Taxes and Charges Template"
		title: Template title
		company: Company name
		rate: Tax rate
		account: Account head
		description: Tax description
	"""
	# Check if template already exists for this company
	existing = frappe.db.exists(doctype, {"title": title, "company": company})
	if existing:
		return

	# Verify account exists
	if not frappe.db.exists("Account", account):
		print("[WARNING]",f"Account {account} not found, skipping template {title}")
		return

	doc = frappe.get_doc({
		"doctype": doctype,
		"title": title,
		"company": company,
		"tax_category": "Tunisia",
		"taxes": [{
			"charge_type": "On Net Total",
			"account_head": account,
			"description": description,
			"rate": rate,
			"included_in_print_rate": 0,
			"included_in_paid_amount": 0
		}]
	})
	doc.insert(ignore_permissions=True)
	print(f"Created template: {title} for {company}")


# Whitelisted function for manual setup
@frappe.whitelist()
def setup_taxes_for_company(company):
	"""
	Manually set up taxes for a specific company.
	Can be called from the UI or console.

	Args:
		company: Company name
	"""
	company_doc = frappe.get_doc("Company", company)

	if company_doc.country != "Tunisia":
		frappe.throw(_("This function is only for Tunisian companies"))

	create_tax_category()
	setup_company_taxes(company, company_doc.abbr)
	frappe.db.commit()

	return _("Tunisian tax configuration completed for {0}").format(company)
