# Email Finder

A command line program that takes an internet domain name (i.e. “jana.com”) and prints out a list of the email addresses that were found on that website.

# Usage

On the command line, run 

```
$ python find-email-addresses.py your-domain.com
```

where your-domain.com is the domain to search, e.g. `jana.com` or `web.mit.edu`. Additionally, you can add a `-s` flag if you want to search subdomains of the entered domain as well.

The program will print emails as it finds them.

**Note:** Requires Python 3
