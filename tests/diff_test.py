from data_helpers.diff import diff_dicts


class TestCompareDicts:

    def test_should_return_differences_simple(self):
        ain = {
            "foo": "bar",
            "hello": "world"
        }
        bin = {
            "foo": "bar",
            "hello": "earth"
        }
        diff = diff_dicts('fieldex', ain, bin)
        assert diff == ['fieldex.hello: world -> earth']

    def test_should_return_differences_nones(self):
        ain = {
            "foo": "bar",
            "hello": None
        }
        bin = {
            "foo": "bar",
            "hello": None
        }
        diff = diff_dicts('fieldex', ain, bin)
        assert diff == []


    def test_should_handle_similar_floats(self):
        ain = {
            "foo": "bar",
            "hello": 10/3,
            "goodbye": 3.33333,
            "world": 3.3
        }
        bin = {
            "foo": "bar",
            "hello": 3.33333333,
            "goodbye": 3.333,
            "world": 3.333333333333
        }
        diff = diff_dicts('fieldex', ain, bin)
        assert diff == ['fieldex.world: 3.3 -> 3.333333333333']

    def test_should_return_differences_nested_dict(self):
        ain = {
            "foo": "bar",
            "hello": {
                "world": 1,
            }
        }
        bin = {
            "foo": "bar",
            "hello": {
                "world": 2,
            }
        }
        diff = diff_dicts('fieldex', ain, bin)
        assert diff == ['fieldex.hello.world: 1 -> 2']

    def test_should_return_differences_nested_dict_added_field(self):
        ain = {
            "foo": "bar",
            "hello": {
                "world": 1,
            }
        }
        bin = {
            "foo": "bar",
            "hello": {
                "earth": 2,
            }
        }
        diff = sorted(diff_dicts('fieldex', ain, bin))
        assert diff == ['fieldex.hello.earth: None -> 2', 'fieldex.hello.world: 1 -> None']

    def test_should_return_differences_list(self):
        ain = {
            "foo": "bar",
            "hello": ["world"],
        }
        bin = {
            "foo": "bar",
            "hello": ["earth"],
        }
        diff = diff_dicts('fieldex', ain, bin)
        assert diff == ['fieldex.hello.0: world -> earth']
