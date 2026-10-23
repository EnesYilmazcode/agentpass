from __future__ import annotations

import pytest

from agentpass.fingerprint import chrome_headers


EXPECTED_KEYS = {
    "user-agent",
    "sec-ch-ua",
    "sec-ch-ua-mobile",
    "sec-ch-ua-platform",
    "accept",
    "accept-language",
}


def test_default_headers_are_coherent_desktop_chrome() -> None:
    headers = chrome_headers()

    assert set(headers) == EXPECTED_KEYS
    assert headers["sec-ch-ua"] == (
        '"Chromium";v="141", "Google Chrome";v="141", '
        '"Not?A_Brand";v="24"'
    )
    assert "Chrome/141.0.0.0" in headers["user-agent"]
    assert headers["sec-ch-ua-mobile"] == "?0"
    assert headers["sec-ch-ua-platform"] == '"Windows"'
    assert all("Headless" not in value for value in headers.values())


def test_custom_version_uses_its_major_version_for_client_hints() -> None:
    headers = chrome_headers("142.3")

    assert "Chrome/142.3.0.0" in headers["user-agent"]
    assert '"Google Chrome";v="142"' in headers["sec-ch-ua"]


@pytest.mark.parametrize("version", ["", "stable", "v141"])
def test_invalid_version_is_rejected(version: str) -> None:
    with pytest.raises(ValueError):
        chrome_headers(version)
