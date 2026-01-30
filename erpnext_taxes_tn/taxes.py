"""
Tunisian VAT/TVA Business Logic
================================

This module contains the core business logic for applying Tunisian VAT rules
to Sales Invoices and Purchase Invoices in ERPNext.

Author: Your Name
License: MIT
"""

import frappe
from frappe import _


def apply_tunisia_tva(doc, method=None):
	"""
	Main function to apply Tunisian VAT rules to invoices.
	
	This function is called via hooks on Sales Invoice and Purchase Invoice
	before_save events.
	
	Business Rules:
	1. If customer/supplier country = Tunisia → Apply local VAT (19% default)
	2. If customer country ≠ Tunisia (export) → Apply 0% VAT
	3. If item has specific tax template → Use item's tax rate
	4. Respect manually selected tax templates (don't override if already set)
	
	Args:
		doc: The Sales Invoice or Purchase Invoice document
		method: The event method (before_save, etc.)
	"""
	
	# Only process if taxes are not already set manually
	# This allows users to override automatic tax selection if needed
	if doc.taxes_and_charges:
		# Tax template already selected, don't override
		return
	
	# Determine if this is a sales or purchase invoice
	is_sales = doc.doctype == "Sales Invoice"
	
	# Get the party (customer or supplier)
	party_type = "Customer" if is_sales else "Supplier"
	party_name = doc.customer if is_sales else doc.supplier
	
	if not party_name:
		# No party selected yet, skip
		return
	
	# Get party country
	party = frappe.get_doc(party_type, party_name)
	party_country = party.country
	
	# Determine which tax template to apply
	tax_template = get_tax_template(
		party_country=party_country,
		is_sales=is_sales,
		company=doc.company
	)
	
	if tax_template:
		# Apply the tax template
		doc.taxes_and_charges = tax_template
		
		# Clear existing taxes and reload from template
		doc.taxes = []
		doc.set_taxes()
		
		# Log the action for debugging
		frappe.logger().info(
			f"Applied tax template '{tax_template}' to {doc.doctype} {doc.name}"
		)


def get_tax_template(party_country, is_sales, company):
	"""
	Determine the appropriate tax template based on party country and transaction type.
	
	Args:
		party_country: Country of the customer or supplier
		is_sales: True for sales, False for purchases
		company: The company name
		
	Returns:
		str: Name of the tax template to apply, or None
	"""
	
	# Check if party is in Tunisia
	is_local = party_country == "Tunisia"
	
	# Determine template prefix
	template_type = "Sales" if is_sales else "Purchase"
	
	if is_local:
		# Local transaction - apply standard 19% VAT
		template_name = f"Tunisia - {template_type} TVA 19%"
	else:
		# Export/Import transaction
		if is_sales:
			# Export - 0% VAT
			template_name = "Tunisia - Export TVA 0%"
		else:
			# Import - typically no automatic tax, let user decide
			# Could be handled differently based on customs rules
			return None
	
	# Verify the template exists
	if frappe.db.exists(f"{template_type} Taxes and Charges Template", template_name):
		return template_name
	else:
		frappe.logger().warning(
			f"Tax template '{template_name}' not found. Please ensure fixtures are installed."
		)
		return None


def validate_tax_amounts(doc, method=None):
	"""
	Optional validation function to ensure tax calculations are correct.
	
	This can be used to add additional validation logic if needed.
	
	Args:
		doc: The Sales Invoice or Purchase Invoice document
		method: The event method
	"""
	
	# Example: Verify that export invoices have 0% tax
	if doc.doctype == "Sales Invoice":
		customer = frappe.get_doc("Customer", doc.customer)
		if customer.country != "Tunisia":
			# This is an export
			total_tax = sum(tax.tax_amount for tax in doc.taxes)
			if total_tax > 0:
				frappe.msgprint(
					_("Warning: Export invoice has non-zero tax amount. Please verify."),
					indicator="orange"
				)


def get_item_tax_rate(item_code, tax_category="Tunisia"):
	"""
	Get the tax rate for a specific item.
	
	This function can be used to retrieve item-specific tax rates
	for items that have special VAT treatment (13%, 7%, or exempt).
	
	Args:
		item_code: The item code
		tax_category: The tax category (default: "Tunisia")
		
	Returns:
		dict: Tax rates for the item, or None
	"""
	
	item = frappe.get_doc("Item", item_code)
	
	# Check if item has a specific tax template
	for tax in item.taxes:
		if tax.tax_category == tax_category:
			return {
				"tax_category": tax.tax_category,
				"item_tax_template": tax.item_tax_template
			}
	
	return None


def apply_item_specific_taxes(doc, method=None):
	"""
	Apply item-specific tax rates if items have special tax templates.
	
	This function checks each item in the invoice and applies
	item-specific tax rates (e.g., 13%, 7%, or 0% for certain products).
	
	Args:
		doc: The Sales Invoice or Purchase Invoice document
		method: The event method
	"""
	
	# Check if any items have specific tax templates
	has_special_taxes = False
	
	for item in doc.items:
		item_tax = get_item_tax_rate(item.item_code)
		if item_tax and item_tax.get("item_tax_template"):
			has_special_taxes = True
			# Apply item tax template
			item.item_tax_template = item_tax["item_tax_template"]
	
	if has_special_taxes:
		# Recalculate taxes with item-specific rates
		doc.calculate_taxes_and_totals()


# Utility functions for tax calculation

def get_tunisia_tax_rates():
	"""
	Get all available Tunisian tax rates.
	
	Returns:
		dict: Dictionary of tax rates
	"""
	return {
		"standard": 19.0,
		"reduced": 13.0,
		"super_reduced": 7.0,
		"zero": 0.0
	}


def is_export_transaction(doc):
	"""
	Check if a transaction is an export (for Sales Invoice).
	
	Args:
		doc: The Sales Invoice document
		
	Returns:
		bool: True if export, False otherwise
	"""
	if doc.doctype != "Sales Invoice":
		return False
	
	if not doc.customer:
		return False
	
	customer = frappe.get_doc("Customer", doc.customer)
	return customer.country != "Tunisia"


def is_import_transaction(doc):
	"""
	Check if a transaction is an import (for Purchase Invoice).
	
	Args:
		doc: The Purchase Invoice document
		
	Returns:
		bool: True if import, False otherwise
	"""
	if doc.doctype != "Purchase Invoice":
		return False
	
	if not doc.supplier:
		return False
	
	supplier = frappe.get_doc("Supplier", doc.supplier)
	return supplier.country != "Tunisia"
