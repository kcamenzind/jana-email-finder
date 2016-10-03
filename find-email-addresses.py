from urllib.request import urlopen, HTTPError
import sys
import re

class EmailFinder():
    """
    An object that will print out a list of all emails found under a 
    given domain, including under discoverable sites.

    :param domain: the domain to find emails under
    """
    def __init__(self, domain):
        if domain.endswith('/'):
            self.domain = domain[:len(domain)-1]
        else:
            self.domain = domain
        self.emails = set()
        self.visited_uris = set()
        self.uri_stack = [self.domain]

    def find_emails(self, allow_subdomains=False):
        """
        Prints all emails listed under the same domain as this
        EmailFinder.

        :param allow_subdomains: searches for emails under 
            subdomains of this EmailFinder's domain
        """
        while len(self.uri_stack) > 0:
            uri = self.uri_stack.pop()

            # only process the uri if we've never visited it before
            if uri not in self.visited_uris:
                self.visited_uris.add(uri)

                try:
                    response = urlopen('http://' + uri)

                    # we won't try to get email from non-text pages 
                    if 'text' in response.getheader('Content-Type'):                    

                        content = response.read().decode('utf-8')

                        self._get_emails(content)
                        self._add_uris(content)

                # if the url isn't actually a valid url, we can just ignore it for now
                # (would ideally do something more sophisticated)
                except (ValueError, HTTPError) as e:
                    pass

        if len(self.emails) == 0:
            return 0
        else:
            return 1

    def _get_emails(self, content):
        email_pattern = '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        possible_emails = re.findall(email_pattern, content)
        for email in possible_emails:
            if self._is_valid_email(email):
                if email not in self.emails:
                    self.emails.add(email)
                    print(email)

    def _is_valid_email(self, email):
        """ 
        Makes sure that the email is a valid address 
        (In this case, just makes sure that there are no leading or 
        trailing dots, or multiple dots in a row, but could be more rigorous)

        :param email: a string of the email to check
        :return: whether the email has valid periods
        """
        local = email.split('@')[0]
        domain = email.split('@')[1]
        
        if local.startswith('.') or local.endswith('.') or  \
            email.startswith('.') or email.endswith('.'):
            return False

        if '..' in email:
            return False

        return True

    def _add_uris(self, content):
        """
        Adds any uris discovered in the content to uri_stack
        """
        url_pattern = 'href=[\"|\'][a-zA-Z0-9-._~:\/\?#\[\]@!$&\'()\*\+,;=]+[\"|\']'
        discovered_links = re.findall(url_pattern, content)

        # visit all links (if they're part of the original domain)
        # takes into account when re.findall returns a list of groups
        # rather than just plain strings
        for link_object in discovered_links:
            if type(link_object) is not str:
                for link in link_object:
                    self._get_emails_from_link(link, allow_subdomains)  
            else:
                self._get_emails_from_link(link_object, allow_subdomains)

    def _get_uri(self, raw_link, parent_domain):
        """
        Converts a raw link from an html file into a full uri
        with no preceding protocol
        """
        if raw_link.endswith('/'):
            link = raw_link[6:len(raw_link)-2]
        else:
            link = raw_link[6:len(raw_link)-1]
        if link.startswith('//'):
            return (link[2:], True)
        elif link.startswith('/'):
            return (domain + link, True)
        elif link.startswith('http://'):
            return (link[7:], True)
        elif link.startswith('https://'):
            return (link[8:], True)
        # jana.com seems to have an https:/ with only one forward
        # slash for the redirect page :)
        elif link.startswith('https:/'):
            return (link[7:], True)
        else:
            return (None, False)

    def _get_emails_from_link(self, link, allow_subdomains):
        """
        Takes a raw html link, converts it into a uri, and 
        finds emails recursively if it's in the original domain
        """
        uri, ok = self._get_uri(link, self.domain)
        if ok:
            if allow_subdomains and self.domain in uri:
                self.uri_stack.append(uri)
            elif uri.startswith(self.domain) or \
                uri.startswith('www.' + self.domain):
                self.uri_stack.append(uri)

if __name__ == "__main__":

    # get domain of website to crawl
    domain = sys.argv[1]
    flags = sys.argv[2:]

    # flag that allows searching subdomains
    if '-s' in flags:
        allow_subdomains = True
    else: 
        allow_subdomains = False

    # crawl site and find emails
    print("Finding emails for " + domain + "\n")
    email_finder = EmailFinder(domain)
    emails_found = email_finder.find_emails(allow_subdomains)

    if emails_found == 0:
        print("No emails found")
