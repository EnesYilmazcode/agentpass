"""Chrome HTTP identity values used by the browser harness."""

from __future__ import annotations


def chrome_headers(version: str = "141") -> dict[str, str]:
    """Return a coherent set of desktop Chrome request headers."""
    major = version.split(".", 1)[0]
    if not major.isdigit():
        raise ValueError("version must begin with a numeric Chrome major version")

    return {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 "
            "Safari/537.36"
        ),
        "sec-ch-ua": (
            f'"Chromium";v="{major}", "Google Chrome";v="{major}", '
            '"Not?A_Brand";v="24"'
        ),
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "accept-language": "en-US,en;q=0.9",
    }

