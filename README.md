# UmbRegister-Spoofer

## Background

Since version 6.2.0 Umbraco has shipped with a few macro snippets relating to membership. These allow developers to get started with implementing common membership features such as registration and login. Because these snippets require server-side processing, Umbraco also ships with some surface controllers which are _auto-routed_. This means that the endpoints are exposed on _every_ Umbraco site, regardless of whether they use membership or not. One of these controllers is the `UmbRegisterController` which contains a single method, `HandleRegisterMember`. This method creates a new member in the Umbraco database.

If you don't use membership on the front-end of your site then the worst an attacker can do with this is fill your database up with useless members and potentially cause a denial of service. If you do use membership then it may allow an attacker to bypass your existing registration process and any validation you may be doing as part of it (perhaps you require payment, or maybe you don't have a public registration form at all and you create the members yourself in the backoffice).

Using this method it would also be possible for an attacker to create an account with a different member type than you intended, possibly with elevated privileges (this would actually be possible on any site that binds to the `RegisterModel` in their registration form and passes it directly to the `MembershipHelper.RegisterMember` method).

Umbraco 7.13.0 and 8.0.0 attempted to solve this issue by adding `[ValidateAntiForgeryToken]` attributes on these controllers. However, this only prevented CSRF attacks (see my other repo about `UmbProfileController` for an example). It was still possible to poke `HandleRegisterMember` by grabbing the anti-forgery cookie and token from an existing form on the site.

Umbraco 7.15.0 and 8.1.0 further attempted to solve this in a way I don't fully understand yet, but I've discovered it can be exploited by grabbing both the anti-forgery token and `ufprt` fields from an existing form on the site (as opposted to just the anti-forgery token in previous versions). Interestingly it also possible to use _only_ the anti-forgery token from a form that was created using `Html.BeginForm` (as opposed to `Html.BeginUmbracoForm` - credit to Ronald Barendse for discovering this which prompted me to investigate further).

## Exploitation

This repository contains a Python script which can crawl an Umbraco site to search for anti-forgery tokens and use them to poke the `HandleRegisterMember` endpoint:

```
usage: umbregister_spoofer.py [-h] [--crawl] [--name NAME] [--email EMAIL]
                              [--username USERNAME] [--password PASSWORD]
                              [--type TYPE]
                              URL

Attempt to create an member account on an Umbraco site using the public `HandleRegisterMember` endpoint.

positional arguments:
  URL                   the base URL of the Umbraco site

optional arguments:
  -h, --help            show this help message and exit
  --crawl, -C           crawl the site to find an anti-forgery cookie, token,
                        and ufprt to send with the request
  --name NAME, -n NAME  the new member's name
  --email EMAIL, -e EMAIL
                        the new member's email address
  --username USERNAME, -u USERNAME
                        the new member's username
  --password PASSWORD, -p PASSWORD
                        the new member's password
  --type TYPE, -t TYPE  the member type alias

Note that it is necessary to crawl for the anti-forgery tokens in Umbraco versions 7.13 and up.
```
