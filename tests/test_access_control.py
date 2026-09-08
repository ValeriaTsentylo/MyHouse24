"""Every admin view must reject anonymous visitors.

The test walks the real URLConf instead of a hardcoded list, so a newly added
view is covered the moment it is registered.
"""

import pytest
from django.urls import NoReverseMatch, URLPattern, URLResolver, get_resolver, reverse

# Public by design: auth flows, Django admin, dev tooling, static/media.
PUBLIC_PREFIXES = ("/admin/", "/users/accounts/", "/__debug__/", "/static/", "/media/")
PUBLIC_NAMES = {"account_login", "register", "account_logout"}


def _named_urls():
    urls = []

    def walk(patterns, prefix=""):
        for p in patterns:
            if isinstance(p, URLResolver):
                walk(p.url_patterns, prefix + str(p.pattern))
            elif isinstance(p, URLPattern) and p.name:
                urls.append((p.name, prefix + str(p.pattern)))

    walk(get_resolver().url_patterns)
    return urls


def _reverse(name, pattern):
    for kwargs in ({}, {"pk": 1}, {"house_id": 1}, {"user_id": 1}, {"apartment_id": 1}):
        try:
            return reverse(name, kwargs=kwargs)
        except NoReverseMatch:
            continue
    return None


PROTECTED = sorted(
    {
        (name, url)
        for name, pattern in _named_urls()
        if name not in PUBLIC_NAMES
        and (url := _reverse(name, pattern))
        and not url.startswith(PUBLIC_PREFIXES)
    }
)


def test_url_discovery_found_views():
    assert PROTECTED, "URLConf walk returned nothing — the test itself is broken"


@pytest.mark.django_db
@pytest.mark.parametrize("name,url", PROTECTED, ids=[n for n, _ in PROTECTED])
def test_anonymous_cannot_reach_admin_views(client, name, url):
    # secure=True so an enabled SECURE_SSL_REDIRECT cannot mask the result
    response = client.get(url, secure=True)
    assert response.status_code in (302, 403), (
        f"{name} ({url}) returned {response.status_code} to an anonymous user"
    )
    if response.status_code == 302:
        assert "login" in response["Location"], (
            f"{name} redirected to {response['Location']} instead of the login page"
        )
