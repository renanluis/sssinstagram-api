from dataclasses import dataclass
import hashlib
import time
from urllib.parse import ParseResult, urlparse
import requests


@dataclass
class Signature:
    ts: int
    _ts: int
    _s: str


@dataclass
class SSSInstagram:
    INSTAGRAM_DOMAINS: tuple[str] = ("instagram.com", "www.instagram.com")
    BASE_URL: str = "https://sssinstagram.com"
    SECRET_KEY: str = "1480053078d494e109c932301998d19f9a00253c5082a734d71f6e336442d209"
    _TS: int = 1746520083801
    LINK_CHUNK_JS_ENDPOINT: str = "js/link.chunk.js"
    API_CONVERT_ENDPOINT: str = "api/convert"

    @classmethod
    def _request(cls, method: str, endpoint: str, **kwargs) -> requests.Response:
        url: str = f"{cls.BASE_URL}/{endpoint}"
        return requests.request(method, url, **kwargs)

    @classmethod
    def _is_valid_url(cls, url: str) -> bool:
        try:
            parsed_url: ParseResult = urlparse(url)
            domain: str = parsed_url.netloc.lower()
            return domain in cls.INSTAGRAM_DOMAINS
        except Exception as e:
            pass

        return False

    @classmethod
    def _generate_signature(cls, url: str):
        msec: int = int(time.time() * 1000)
        data_str: str = f"{url}{msec}{cls.SECRET_KEY}"
        data: str = data_str.encode("utf-8")

        hash_object: hashlib.HASH = hashlib.sha256(data)
        hex_hash: str = hash_object.hexdigest()

        return Signature(ts=msec, _ts=cls._TS, _s=hex_hash)

    @classmethod
    def ssig(cls, url: str):
        if not cls._is_valid_url(url):
            raise f"Invalid Instagram URL."

        _signature: Signature = cls._generate_signature(url)
        response: requests.Response = cls._request(
            "POST",
            cls.API_CONVERT_ENDPOINT,
            json={
                "url": url,
                "ts": _signature.ts,
                "_ts": _signature._ts,
                "_s": _signature._s,
            },
        )
        response.raise_for_status()
        return response.json()
