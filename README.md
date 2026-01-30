# ERPNext Tunisian VAT/TVA App

Custom ERPNext application for implementing Tunisian VAT (TVA) rules in ERPNext v15/v16.

## 🎯 Features

- **Automatic VAT Application**: Automatically applies correct VAT rates based on customer/supplier country
- **Multiple VAT Rates**: Supports all Tunisian VAT rates:
  - 19% (Standard)
  - 13% (Reduced)
  - 7% (Super Reduced)
  - 0% (Export/Exempt)
- **Export Handling**: Automatically applies 0% VAT for export transactions
- **Item-Specific Taxes**: Support for items with special tax rates
- **No Core Modifications**: Clean implementation using Frappe hooks and fixtures
- **Multi-Tenant Ready**: Compatible with SaaS/multi-site deployments

## 📋 Requirements

- ERPNext v15 or v16
- Frappe Framework
- Python 3.10+

## 🚀 Installation

### Step 1: Get the App

```bash
cd /path/to/your/frappe-bench
bench get-app /path/to/erpnext_taxes_tn
```

### Step 2: Install on Site

```bash
bench --site your-site.local install-app erpnext_taxes_tn
```

### Step 3: Run Migrations

```bash
bench --site your-site.local migrate
```

### Step 4: Restart Bench

```bash
bench restart
```

## ⚙️ Configuration

### 1. Verify Tax Accounts

Before using the app, ensure you have the following tax accounts in your Chart of Accounts:

- TVA 19% - TN
- TVA 13% - TN
- TVA 7% - TN
- TVA 0% - TN

You can create these under: **Accounting > Chart of Accounts**

### 2. Set Tax Category

For customers and suppliers in Tunisia, set the Tax Category to "Tunisia" in their master records.

### 3. Configure Default Tax Templates (Optional)

You can set default tax templates in Company settings or let the app automatically select them.

## 📖 Usage

### Automatic Tax Application

The app automatically applies the correct tax template when you:

1. **Create a Sales Invoice**:
   - If customer country = Tunisia → Applies TVA 19%
   - If customer country ≠ Tunisia → Applies TVA 0% (Export)

2. **Create a Purchase Invoice**:
   - If supplier country = Tunisia → Applies TVA 19%
   - If supplier country ≠ Tunisia → No automatic tax (manual selection required)

### Item-Specific Tax Rates

For items that require special VAT rates (13%, 7%, or exempt):

1. Go to the Item master
2. In the "Tax" section, add an Item Tax Template
3. Select the appropriate template (e.g., "Tunisia TVA 13%")
4. The app will automatically apply this rate for that item

### Manual Override

If you need to manually select a different tax template:

1. In the invoice, select the desired template in the "Taxes and Charges" field
2. The app will respect your manual selection and not override it

## 🏗️ Architecture

```
erpnext_taxes_tn/
├── erpnext_taxes_tn/
│   ├── __init__.py
│   ├── hooks.py              # App configuration and event hooks
│   ├── taxes.py              # Core business logic
│   └── fixtures/             # Tax configuration fixtures
│       ├── tax_category.json
│       ├── item_tax_template.json
│       ├── sales_taxes_and_charges_template.json
│       ├── purchase_taxes_and_charges_template.json
│       └── tax_rule.json
├── pyproject.toml
├── README.md
└── license.txt
```

## 🔧 Customization

### Adding New Tax Rates

To add a new tax rate:

1. Create a new Item Tax Template in ERPNext
2. Create corresponding Sales/Purchase Taxes and Charges Templates
3. Add the templates to the fixtures in `hooks.py`
4. Export the fixtures: `bench --site your-site.local export-fixtures`

### Modifying Business Logic

The main business logic is in `taxes.py`. Key functions:

- `apply_tunisia_tva()`: Main hook function
- `get_tax_template()`: Determines which template to apply
- `get_item_tax_rate()`: Retrieves item-specific tax rates

## 🧪 Testing

### Test Local Sales

1. Create a Sales Invoice
2. Select a customer with country = "Tunisia"
3. Add items
4. Verify TVA 19% is applied

### Test Export Sales

1. Create a Sales Invoice
2. Select a customer with country ≠ "Tunisia"
3. Add items
4. Verify TVA 0% is applied

### Test Item-Specific Rates

1. Set an item's tax template to "Tunisia TVA 13%"
2. Create a Sales Invoice with that item
3. Verify TVA 13% is applied for that item

## 🐛 Troubleshooting

### Tax Template Not Applied

**Issue**: Tax template is not automatically applied

**Solutions**:
- Verify the customer/supplier has a country set
- Check that tax accounts exist in Chart of Accounts
- Ensure fixtures were loaded during installation
- Check if a tax template is already manually selected (app won't override)

### Fixtures Not Loaded

**Issue**: Tax templates don't appear after installation

**Solutions**:
```bash
# Re-run migrations
bench --site your-site.local migrate

# Or manually import fixtures
bench --site your-site.local import-doc fixtures/tax_category.json
```

### Wrong Tax Rate Applied

**Issue**: Incorrect tax rate is being applied

**Solutions**:
- Verify the Tax Rules are configured correctly
- Check the customer/supplier country
- Review item-specific tax templates
- Check logs: `bench --site your-site.local console` then `frappe.log_error()`

## 📚 Additional Resources

- [ERPNext Documentation](https://docs.erpnext.com)
- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [Tunisian Tax Authority](https://www.impots.finances.gov.tn/)

## 📄 License

MIT License - See [license.txt](license.txt) for details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions:
- Create an issue in the repository
- Contact: your.email@example.com

## 🔄 Version History

### v1.0.0 (2026-01-30)
- Initial release
- Support for all Tunisian VAT rates (19%, 13%, 7%, 0%)
- Automatic tax application for Sales and Purchase Invoices
- Export handling
- Item-specific tax rates
