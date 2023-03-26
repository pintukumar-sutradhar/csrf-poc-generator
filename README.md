#csrf-poc-generator


The csrf-poc-generator is a Python script that can be used to test for Cross-Site Request Forgery (CSRF) vulnerabilities on a website. The script crawls the website up to a specified depth and generates a proof-of-concept (POC) HTML page for each form found on each page.

Usage:
1. Clone the repository: git clone https://github.com/pintukumar-sutradhar/csrf_poc_generator
2. Install the required packages: pip install -r requirements.txt
3. Run the script: python csrf_poc_generator.py <url> [-d <depth>]

Options
1. < url >: the URL of the website to test.
2. -d <depth>: the depth to crawl the website (optional, default is 2).

Disclaimer
This tool is intended for educational purposes only and should not be used to test websites without the owner's permission. The author is not responsible for any misuse of the tool.
