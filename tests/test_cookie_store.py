"""Regression tests for cookie_store module."""
from nodeseek_signin.cookie_store import _as_dict, _data_list, _is_ok, _msg


class TestAsDict:
    def test_dict_passthrough(self):
        assert _as_dict({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_non_string_keys_filtered(self):
        assert _as_dict({1: "a", "b": "c"}) == {"b": "c"}

    def test_non_mapping_returns_none(self):
        assert _as_dict("not a dict") is None
        assert _as_dict(42) is None
        assert _as_dict(None) is None

    def test_empty_dict(self):
        assert _as_dict({}) == {}


class TestIsOk:
    def test_code_200(self):
        assert _is_ok({"code": 200}) is True

    def test_code_not_200(self):
        assert _is_ok({"code": 400}) is False

    def test_missing_code(self):
        assert _is_ok({}) is False

    def test_non_mapping(self):
        assert _is_ok("invalid") is False


class TestDataList:
    def test_normal_list(self):
        result = {"data": [{"id": 1}, {"id": 2}]}
        assert _data_list(result) == [{"id": 1}, {"id": 2}]

    def test_non_list_data(self):
        assert _data_list({"data": "not list"}) == []

    def test_missing_data(self):
        assert _data_list({}) == []

    def test_non_mapping_items_filtered(self):
        result = {"data": [{"id": 1}, "invalid", {"id": 2}]}
        assert _data_list(result) == [{"id": 1}, {"id": 2}]


class TestMsg:
    def test_message_field(self):
        assert _msg({"message": "test"}) == "test"

    def test_msg_field(self):
        assert _msg({"msg": "fallback"}) == "fallback"

    def test_message_truncated(self):
        long_msg = "x" * 300
        assert len(_msg({"message": long_msg})) == 200

    def test_non_mapping(self):
        result = _msg("invalid")
        assert isinstance(result, str)
