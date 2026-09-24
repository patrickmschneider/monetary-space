"""Shared HTTP session. Some publishers (BoE) reject default client user agents."""
from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = (
    "Mozilla/5.0 (compatible; monetary-space/0.1; "
    "+https://github.com/patrickmschneider/monetary-space)"
)
TIMEOUT = 30


def session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    retry = Retry(total=3, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


def get(url: str, **kwargs) -> requests.Response:
    r = session().get(url, timeout=TIMEOUT, **kwargs)
    r.raise_for_status()
    return r
