import hashlib
import http.client
import json
import pytest
from api_client_executor import (
    ApiClientExecutor,
    TransportError,
    JCSValidationError,
    canonicalize_jcs_from_text,
    hash_canonical_json_text,
    validate_url,
)
PAYLOAD_NFC = """{
  "z_zeta": "último_campo",
  "a_alpha": "primeiro_campo",
  "m_middle": {
    "beta": 2,
    "alpha": 1,
    "unicode_test": "Atenção: café, maçã, ação & naïve 🚀"
  },
  "numbers": {
    "zero_neg": -0,
    "scientific": 1e2,
    "float_zero": 1.0,
    "integer": 42
  },
  "array_test": [3, 1, 2]
}"""
UNICODE_TEST_NFD = (
    "Aten" + "c" + "\u0327" + "a" + "\u0303" + "o" + ": " +
    "cafe" + "\u0301" + ", " +
    "mac" + "\u0327" + "a" + "\u0303" + ", " +
    "ac" + "\u0327" + "a" + "\u0303" + "o" + " & " +
    "nai" + "\u0308" + "ve " + "\U0001F680"
)
PAYLOAD_NFD_OBJ = {
    "z_zeta": "último_campo",
    "a_alpha": "primeiro_campo",
    "m_middle": {"beta": 2, "alpha": 1, "unicode_test": UNICODE_TEST_NFD},
    "numbers": {"zero_neg": -0, "scientific": 1e2, "float_zero": 1.0, "integer": 42},
    "array_test": [3, 1, 2],
}
PAYLOAD_NFD = json.dumps(PAYLOAD_NFD_OBJ, ensure_ascii=False)
EXPECTED_NFC_CANONICAL = (
    '{"a_alpha":"primeiro_campo","array_test":[3,1,2],'
    '"m_middle":{"alpha":1,"beta":2,"unicode_test":"Atenção: café, maçã, ação & naïve 🚀"},'
    '"numbers":{"float_zero":1,"integer":42,"scientific":100,"zero_neg":0},'
    '"z_zeta":"último_campo"}'
)
EXPECTED_NFC_SHA = "2fcbc0df068e1b10be831b0ae1d1577d5b927e1253caad93d79da862aef0c2da"
EXPECTED_NFD_SHA = "76fde4e93c5de6b9212dde968e973fa2ece45e60f88a1b1384511a1f748bba64"
def test_jcs_canonicalization_nfc_001():
    result = hash_canonical_json_text(PAYLOAD_NFC)
    assert result["len_bytes"] == 240
    assert result["canonical_utf8"] == EXPECTED_NFC_CANONICAL
    assert result["sha256"] == EXPECTED_NFC_SHA
def test_jcs_unicode_nfd_divergence_001():
    result_nfc = hash_canonical_json_text(PAYLOAD_NFC)
    result_nfd = hash_canonical_json_text(PAYLOAD_NFD)
    assert result_nfd["len_bytes"] == 248
    assert result_nfd["sha256"] == EXPECTED_NFD_SHA
    assert result_nfc["sha256"] != result_nfd["sha256"]
def test_jcs_numeric_canonicalization_001():
    result = hash_canonical_json_text(PAYLOAD_NFC)
    canon = result["canonical_utf8"]
    assert '"zero_neg":0' in canon
    assert '"scientific":100' in canon
    assert '"float_zero":1' in canon
    assert '"array_test":[3,1,2]' in canon
def test_jcs_duplicate_keys_rejection_001():
    with pytest.raises(JCSValidationError, match="DUPLICATE_KEY"):
        canonicalize_jcs_from_text('{"a": 1, "a": 2}')
    with pytest.raises(JCSValidationError, match="DUPLICATE_KEY"):
        canonicalize_jcs_from_text('{"m": {"alpha": 1, "alpha": 2}}')
def test_jcs_non_json_constants_rejection_001():
    for bad in ['{"v": NaN}', '{"v": Infinity}', '{"v": -Infinity}']:
        with pytest.raises(JCSValidationError):
            canonicalize_jcs_from_text(bad)
def test_dns_empty_raises_dns_empty():
    def empty_resolver(host, port):
        assert port == 443
        return []
    ex = ApiClientExecutor(resolver=empty_resolver)
    with pytest.raises(TransportError, match="DNS_EMPTY"):
        ex.execute("GET", "https://example.com/")
def test_url_userinfo_rejected():
    with pytest.raises(TransportError, match="URL_USERINFO_REJECTED"):
        validate_url("https://user:pass@example.com/")
def test_url_fragment_rejected():
    with pytest.raises(TransportError, match="URL_FRAGMENT_REJECTED"):
        validate_url("https://example.com/#frag")
def test_url_ipv6_ok():
    host, _, port, path = validate_url("https://[::1]:8443/a?b=1")
    assert host == "::1"
    assert port == 8443
    assert path == "/a?b=1"