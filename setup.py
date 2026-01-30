from setuptools import setup, find_packages

with open("erpnext_taxes_tn/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="erpnext_taxes_tn",
    version="1.0.0",
    author="Mehdi Khechine",
    author_email="your.email@example.com",
    description="ERPNext Custom App for Tunisian VAT/TVA Rules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/khechine/erpnext_taxes_tn",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        # frappe is already installed in the bench environment
    ],
    include_package_data=True,
    zip_safe=False,
)
