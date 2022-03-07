
from dataclasses import dataclass
from typing import Any, NamedTuple

from data_helpers.fill_np_array import fill_np_array_with_cls
from data_helpers.dictionary_helpers import ListMergeMethods, get_nested_val, merge_dataclasses, merge_dictionaries


def test_get_nested_args_from_dict():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'bar': {
            'roo': 4,
            'ree': {
                'sow': 10,
            }
        },
        'arr': [1, 2, 3],
        'a': A(),
    }
    result = get_nested_val(data, 'bar.roo')
    assert result == 4
    result = get_nested_val(data, 'bar.ree.sow')
    assert result == 10
    result = get_nested_val(data, 'arr.1')
    assert result == 2
    result = get_nested_val(data, 'a.val')
    assert result == 1


def test_get_nested_args_with_numpy_list():
    class Sub(NamedTuple):
        name: str = 'dave'

    class A(NamedTuple):
        val: int = 1
        sub: Sub = fill_np_array_with_cls(3, Sub)

    data = {
        'a': A(),
    }
    result = get_nested_val(data, 'a.sub.0.name')
    assert result == 'dave'


def test_get_nested_arg_from_list():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'arr': [1, 2, 3],
        'matrix': [[1, 2, 3], [4, 5, 6]]
    }
    result = get_nested_val(data, 'arr.1')
    assert result == 2
    result = get_nested_val(data, 'matrix.1.1')
    assert result == 5


def test_get_nested_arg_from_list_with_wildcard():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'arr': [1, 2, 3],
        'matrix': [[1, 2, 3], [4, 5, 6]],
        'deepmatrix': [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
        'dictlist': [{'foo': 'abc'}, {'foo': 'def'}]
    }
    # result = get_nested_val(data, 'matrix.1.x')
    # assert result == [4, 5, 6]
    result = get_nested_val(data, 'matrix._.1')
    assert result == [2, 5]
    result = get_nested_val(data, 'deepmatrix._.1._')
    assert result == [[3, 4], [7, 8]]
    result = get_nested_val(data, 'dictlist._.foo')


class TestMergeDataclasses:

    @dataclass
    class Inner:
        a: int = None
        b: int = None

    @dataclass
    class Foo:
        foo: int = None
        bar: int = None
        inner: Any = None

    def test_can_merge_nested_dataclasses(self):
        a = self.Foo(foo=1)
        b = self.Foo(bar=1)
        c = merge_dataclasses(a, b)
        assert c.foo == 1
        assert c.bar == 1

    def test_can_merge_nested_dataclasses_left_clash(self):
        a = self.Foo(foo=1)
        b = self.Foo(foo=2, bar=1)
        c = merge_dataclasses(a, b)
        assert c.foo == 2
        assert c.bar == 1

    def test_can_merge_nested_dataclasses_nested(self):
        a = self.Foo(foo=1)
        b = self.Foo(inner=self.Inner(1))
        c = merge_dataclasses(a, b)
        assert c.foo == 1
        assert c.inner.a == 1

    def test_can_merge_nested_dataclasses_nested_clash(self):
        a = self.Foo(foo=1, inner=self.Inner(2))
        b = self.Foo(inner=self.Inner(1))
        c = merge_dataclasses(a, b)
        assert c.foo == 1
        assert c.inner.a == 1

    def test_can_merge_nested_dataclasses_nested_clash_overlap(self):
        a = self.Foo(foo=1, inner=self.Inner(None, 2))
        b = self.Foo(inner=self.Inner(1))
        c = merge_dataclasses(a, b)
        assert c.foo == 1
        assert c.inner.a == 1
        assert c.inner.b == 2


a = {
    "inner": {
        "a": 1,
        "b": 2,
    },
    "foo": 1,
    "bar": 2,
}
b = {
    "inner": {
        "a": 1,
        "b": 2,
    },
    "foo": 1,
    "bar": 2,
}


class TestMergeDictionaries:

    def test_can_merge_nested_dictionaries(self):

        a = {
            "foo": 1,
        }
        b = {
            "bar": 1,
        }
        c = merge_dictionaries(a, b)
        assert c["foo"] == 1
        assert c["bar"] == 1

    def test_can_merge_nested_dictionaries_left_clash(self):
        a = {
            "foo": 1,
        }
        b = {
            "foo": 2,
            "bar": 1,
        }
        c = merge_dictionaries(a, b)
        assert c["foo"] == 2
        assert c["bar"] == 1

    def test_can_merge_nested_dictionaries_nested(self):

        a = {
            "foo": 1,
        }
        b = {
            "inner": {
                "a": 1,
            },
        }

        c = merge_dictionaries(a, b)
        assert c["foo"] == 1
        assert c["inner"]["a"] == 1

    def test_can_merge_nested_dictionaries_nested_clash(self):
        a = {
            "foo": 1,
            "inner": {
                "a": 2,
            }
        }
        b = {
            "inner": {
                "a": 1,
            },
        }

        c = merge_dictionaries(a, b)
        assert c["foo"] == 1
        assert c["inner"]["a"] == 1

    def test_can_merge_nested_dictionaries_nested_clash_overlap(self):
        a = {
            "foo": 1,
            "inner": {
                "a": 2,
                "b": 3,
            }
        }
        b = {
            "inner": {
                "a": 1,
            },
        }

        c = merge_dictionaries(a, b)
        assert c["foo"] == 1
        assert c["inner"]["a"] == 1
        assert c["inner"]["b"] == 3

    def test_can_merge_nested_list(self):
        a = {
            "foo": 1,
            "inner": [
                {
                    "id": 1,
                    "a": 1,
                },
                {
                    "id": 2,
                    "a": 2,
                },
            ]
        }
        b = {
            "foo": 1,
            "inner": [
                {
                    "id": 1,
                    "a": 1,
                },
                {
                    "id": 2,
                    "a": "alt",
                },
            ]
        }

        c = merge_dictionaries(a, b)
        assert c["foo"] == 1
        assert c["inner"][0]["a"] == 1
        assert c["inner"][1]["a"] == "alt"

    def test_can_merge_nested_list_merge_individual_b(self):
        a = {
            "foo": 1,
            "inner": [
                {
                    "id": 1,
                    "a": 99,
                },
                {
                    "id": 2,
                    "a": 2,
                },
            ]
        }
        b = {
            "foo": 1,
            "inner": [
                {
                    "id": 1,
                },
                {
                    "id": 2,
                    "a": "alt",
                },
            ]
        }

        c = merge_dictionaries(a, b, ListMergeMethods.ZIP)
        assert c["foo"] == 1
        assert c["inner"][0]["a"] == 99
        assert c["inner"][1]["a"] == "alt"

    def test_can_merge_nested_list_merge_individual_c(self):
        a = {
            "top": {
                "parameters": [
                    {
                        "name": "hello",
                        "other": "this"
                    }
                ]
            }
        }
        b = {
            "top": {
                "parameters": [
                    {
                        "name": "world"
                    }
                ]
            }
        }

        c = merge_dictionaries(a, b, ListMergeMethods.ZIP)
        assert c["top"]["parameters"][0]["name"] == "world"
        assert c["top"]["parameters"][0]["other"] == "this"


    def test_can_merge_nested_list_merge_individual_e(self):
        a = {
            "top": {
                "parameters": [
                    {
                        "info": {
                            "nested": {
                                "a": 1,
                                "b": 2
                            }
                        }
                    }
                ]
            }
        }
        b = {
            "top": {
                "parameters": [
                    {
                        "info": {
                            "nested": {
                                "a": 2
                            }
                        }
                    }
                ]
            }
        }

        c = merge_dictionaries(a, b, ListMergeMethods.ZIP)
        assert c["top"]["parameters"][0]["info"]["nested"]["a"] == 2
        assert c["top"]["parameters"][0]["info"]["nested"]["b"] == 2


    def test_can_merge_nested_list_merge_individual_d(self):
        a = {
            "top": {
                "parameters": [
                    1,
                    2,
                    3,
                ]
            }
        }
        b = {
            "top": {
                "parameters": [
                    4,
                ]
            }
        }

        c = merge_dictionaries(a, b, ListMergeMethods.ZIP)
        assert len(c["top"]["parameters"]) == 1
        assert c["top"]["parameters"][0] == 4

    # def test_can_merge_nested_list_merge_individual(self):
    #     a = {'COMMENT': 'Bangor Wheat Demo', 'Land_Cover': {'nL': 4, 'layer_height_frac': [...], 'fLAI': [...]}}
    #     b = {'COMMENT': 'Bangor Wheat Demo', 'Met': {'td_base_temperature': 0, 'inputs': {...}}, 'VERSION': 10, 'Location': {'lat': 53, 'lon': 4, 'elev': 5.0, 'albedo': 0.2, 'z_O3': 1.5, 'z_u': 10.0, 'Rsoil': 200, 'start_day': 71}, 'resistance': {'rsur_calc_method': 'multi_layer', 'rext_calc_method': 'const'}, 'soil_moisture': {'soil_texture': 'loam', 'soil': {...}, 'root': 0.4, 'pwp': -4.0, 'asw_fc': None, 'source': 'external input SWC', 'initial_swc': None}, 'carbon_allocation': {'use_carbon_allocation': True, 'a_root': 18.5, 'a_stem': 16.0, 'a_leaf': 18.0, 'b_root': -20.0, 'b_stem': -15.0, 'b_leaf': -18.5, 'gamma': 27.3, 'delta': -0.0507, ...}, 'Land_Cover': {'nL': 1, 'nP': 3, 'layer_height_frac': [...], 'height_method': 'carbon', 'LAI_method': 'carbon', 'LAI_distribution_method': 'fraction', 'leaf_emergence_multiplier': 1.8, 'SAI_method': 'estimate total', 'dvi_method': 'JULES'}}

    #     c = merge_dictionaries(a, b, ListMergeMethods.ZIP)
    #     assert c["Land_Cover"]["fLAI"] == [0.25,0.25,0.25,0.25]



