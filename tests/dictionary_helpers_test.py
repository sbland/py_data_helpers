
from dataclasses import dataclass
from typing import Any, NamedTuple

from data_helpers.fill_np_array import fill_np_array_with_cls
from data_helpers.dictionary_helpers import (
    ListMergeMethods,
    get_nested_val,
    merge_dataclasses,
    merge_dictionaries,
    find_key,
    find_all_keys,
)


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

    def test_can_merge_nested_list_merge_individual_null_combined(self):
        a = {
            "top": {
                "parameters": [
                    {
                        "info": {
                            "nested": {
                                "a": None,
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
                                "a": None
                            }
                        }
                    }
                ]
            }
        }

        c = merge_dictionaries(a, b, ListMergeMethods.ZIP)
        assert c["top"]["parameters"][0]["info"]["nested"]["a"] == None

    def test_can_merge_nested_list_merge_individual_null_list(self):
        a = {
            "top": {
                "parameters": None
            }
        }
        b = {
            "top": {
                "parameters": None
            }
        }

        c = merge_dictionaries(a, b, ListMergeMethods.ZIP)
        assert c["top"]["parameters"] == None

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


class TestFindKey:

    def test_find_nested_key(self):
        k = "foo"
        d = {
            "bar": {
                "foo": 2,
                "roo": 3,
                "ree": {
                    "foo": 4,
                    "sow": 5,
                }
            }
        }
        k_out = find_key(d, k)
        assert k_out == "bar.foo"

    def test_find_nested_key_in_list(self):
        k = "foo"
        d = {
            "bar": [{
                "barbar": 2,
                "roo": 3,
            },
                {
                "foo": 2,
                "roo": 3,
            }]
        }
        k_out = find_key(d, k)
        assert k_out == "bar.1.foo"

    def test_long_examples(self):
        k = "t_b"
        d = {'VERSION': 11,
             'id': 'MISSING_ID',
             'notes': '',
             'Land_Cover': {'nL': 4,
                            'nLC': 1,
                            'nP': 1,
                            'primary_LC': 0,
                            'land_cover_type': 'CROP',
                            'parameters': [{'name': 'Bangor Wheat',
                                            'phenology': {'PRESET': 'WHEAT_SPRING',
                                                          'fphen_intervals': [[0, 0],
                                                                              [66.25, 0],
                                                                              [265.0, 1],
                                                                              [1100.0, 1],
                                                                              [1325.0, 0]],
                                                          'leaf_fphen_intervals': [[0, 0],
                                                                                   [1015.0000000000001, 0],
                                                                                   [1015.0000000000001, 1],
                                                                                   [1100.0, 1],
                                                                                   [1166.25, 1],
                                                                                   [1391.5, 0.7],
                                                                                   [1325.0, 0],
                                                                                   [1325.0, 0]],
                                                          'dvi_interval': [[0, -1.000000001],
                                                                           [66.25, 0.0],
                                                                           [1015.0, 1.0],
                                                                           [1325.0, 2.0]],
                                                          'key_dates': {'sowing': 318,
                                                                        'emergence': None,
                                                                        'harvest': None,
                                                                        'Astart': None,
                                                                        'Aend': None,
                                                                        'mid_anthesis': None},
                                                          'key_dates_td': {'sowing': 0,
                                                                           'emergence': 66.25,
                                                                           'harvest': 1325,
                                                                           'Astart': 1015,
                                                                           'Aend': 1325.0,
                                                                           'mid_anthesis': 1100},
                                                          'key_lengths': {'sowing_to_emerge': None,
                                                                          'sowing_to_f_phen_b': None,
                                                                          'sowing_to_f_phen_c': None,
                                                                          'sowing_to_astart': None,
                                                                          'sowing_to_end': None,
                                                                          'emerg_to_astart': None,
                                                                          'emerg_to_end': None,
                                                                          'emerg_to_veg': None,
                                                                          'veg_to_harvest': None},
                                                          'key_lengths_td': {'sowing_to_emerge': 66.25,
                                                                             'sowing_to_f_phen_b': 265.0,
                                                                             'sowing_to_f_phen_c': 1100.0,
                                                                             'sowing_to_astart': 1015.0000000000001,
                                                                             'sowing_to_end': 1325,
                                                                             'emerg_to_astart': 948.7500000000001,
                                                                             'emerg_to_end': 1258.75,
                                                                             'emerg_to_veg': 948.75,
                                                                             'veg_to_harvest': 310.0},
                                                          'key_lengths_leaf': {'tl': None,
                                                                               'tl_em': None,
                                                                               'tl_ma': None,
                                                                               'tl_ep': None,
                                                                               'tl_se': None,
                                                                               'leaf_f_phen_e': None,
                                                                               'leaf_f_phen_g': None,
                                                                               'leaf_f_phen_h': None,
                                                                               'leaf_f_phen_i': None,
                                                                               'plant_emerg_to_leaf_emerg': None,
                                                                               'leaf_emerg_to_astart': None,
                                                                               'astart_to_senescence': None},
                                                          'key_lengths_leaf_td': {'tl': 1.5083352514580678e-13,
                                                                                  'tl_em': 1.1368683772161603e-13,
                                                                                  'tl_ma': 3.7146687424190737e-14,
                                                                                  'tl_ep': 0.0,
                                                                                  'tl_se': 0.0,
                                                                                  'leaf_f_phen_e': None,
                                                                                  'leaf_f_phen_g': None,
                                                                                  'leaf_f_phen_h': None,
                                                                                  'leaf_f_phen_i': None,
                                                                                  'plant_emerg_to_leaf_emerg': None,
                                                                                  'leaf_emerg_to_astart': None,
                                                                                  'astart_to_senescence': None},
                                                          'key_lengths_flag_leaf': {'tl': None,
                                                                                    'tl_em': None,
                                                                                    'tl_ma': None,
                                                                                    'tl_ep': None,
                                                                                    'tl_se': None,
                                                                                    'leaf_f_phen_e': None,
                                                                                    'leaf_f_phen_g': None,
                                                                                    'leaf_f_phen_h': None,
                                                                                    'leaf_f_phen_i': None,
                                                                                    'plant_emerg_to_leaf_emerg': None,
                                                                                    'leaf_emerg_to_astart': None,
                                                                                    'astart_to_senescence': None},
                                                          'key_lengths_flag_leaf_td': {'tl': 1258.75,
                                                                                       'tl_em': 948.75,
                                                                                       'tl_ma': 309.99999999999994,
                                                                                       'tl_ep': 206.66666666666663,
                                                                                       'tl_se': 103.33333333333331,
                                                                                       'leaf_f_phen_e': 84.99999999999999,
                                                                                       'leaf_f_phen_g': 66.25,
                                                                                       'leaf_f_phen_h': 291.5,
                                                                                       'leaf_f_phen_i': 224.99999999999994,
                                                                                       'plant_emerg_to_leaf_emerg': 1.1368683772161603e-13,
                                                                                       'leaf_emerg_to_astart': None,
                                                                                       'astart_to_senescence': None},
                                                          'LAI_a': None,
                                                          'LAI_b': None,
                                                          'LAI_c': None,
                                                          'LAI_d': None,
                                                          'LAI_1': None,
                                                          'LAI_2': None,
                                                          'SAI_method': 'LAI_max',
                                                          'f_phen_method': 'tt day PLF',
                                                          'leaf_f_phen_method': 'tt day PLF',
                                                          'day_fphen_plf': {'f_phen_limA': None,
                                                                            'f_phen_limB': None,
                                                                            'f_phen_a': None,
                                                                            'f_phen_b': None,
                                                                            'f_phen_c': None,
                                                                            'f_phen_d': None,
                                                                            'f_phen_e': None,
                                                                            'f_phen_1': None,
                                                                            'f_phen_2': None,
                                                                            'f_phen_3': None,
                                                                            'f_phen_4': None,
                                                                            'leaf_f_phen_a': None,
                                                                            'leaf_f_phen_b': None,
                                                                            'leaf_f_phen_c': None,
                                                                            'leaf_f_phen_1': None,
                                                                            'leaf_f_phen_2': None},
                                                          'f_phen_min': 0,
                                                          'leaf_f_phen_a': 0.3,
                                                          'leaf_f_phen_b': 0.7,
                                                          'f_Astart': 0.7660377358490567,
                                                          'f_mid_anthesis': 0.8301886792452831,
                                                          'f_fphen_1_ets': 0.0641509433962264,
                                                          'f_fphen_3_ets': 0.05,
                                                          'f_fphen_4_ets': 0.22,
                                                          'f_fphen_5_ets': 0.16981132075471694,
                                                          'f_t_lem': 0.7160377358490566,
                                                          'f_t_lma': 0.23396226415094334,
                                                          'f_t_lep': 0.15597484276729556,
                                                          'f_t_lse': 0.07798742138364778,
                                                          'f_t_lse_mature': 0.33,
                                                          'f_fphen_a': 0.05,
                                                          'f_fphen_b': 0.2,
                                                          'f_fphen_c': 0.8301886792452831,
                                                          'f_fphen_d': 1.0,
                                                          'f_tt_emr': 0.05,
                                                          'f_tt_veg': 0.7160377358490566,
                                                          'f_tt_rep': 0.2339622641509434,
                                                          'f_leaf_f_fphen': 0.23396226415094334,
                                                          'v_T_max': 35.87034127062043,
                                                          'v_T_min': 15.558863583008138,
                                                          'PIV': 0.912629759,
                                                          'lat_f_k': None,
                                                          'lat_f_b': None,
                                                          'lat_f_c': None},
                                            'gsto': {'method': 'photosynthesis',
                                                     'Tleaf_method': 'ambient',
                                                     'fmin': 0.01,
                                                     'f_VPD_method': 'danielsson',
                                                     'VPD_crit': 8.0,
                                                     'VPD_min': 3.2,
                                                     'VPD_max': 1.2,
                                                     'f_SW_method': 'disabled',
                                                     'SWP_min': -1.25,
                                                     'SWP_max': -0.05,
                                                     'fSWP_exp_curve': 'temperate',
                                                     'fSWP_exp_a': 0.355,
                                                     'fSWP_exp_b': -0.706,
                                                     'ASW_min': 0.0,
                                                     'ASW_max': 50.0},
                                            'multip_gsto': {'f_light_method': 'disabled',
                                                            'f_lightfac': 0.006,
                                                            'f_temp_method': 'disabled',
                                                            'T_min': None,
                                                            'T_opt': None,
                                                            'T_max': None,
                                                            'gmax': None,
                                                            'gmorph': 1.0,
                                                            'f_O3_method': 'disabled'},
                                            'pn_gsto': {'g_sto_0': 10000.0,
                                                        'm': 3.5,
                                                        'use_O3_damage': True,
                                                        'senescence_method': 'ewert',
                                                        'V_J_method': 'constant',
                                                        'V_cmax_25': 137,
                                                        'J_max_25': 228,
                                                        'V_cmax_25_kN': 0.2,
                                                        'R_d_coeff': 0.01,
                                                        'r_g': 0.16,
                                                        'D_0_method': 'constant',
                                                        'D_0': 2.2,
                                                        'co2_concentration_balance_threshold': 0.001,
                                                        'co2_concentration_max_iterations': 50,
                                                        'K_z': 24,
                                                        'F_0': 37,
                                                        'leaf_f_phen_Anet_influence': 'disabled',
                                                        't_b': -0.257838202,
                                                        't_o': 17.79866132,
                                                        't_m': 23.8743407,
                                                        'p_crit': 24,
                                                        'p_sens': 0,
                                                        'tt_emr': None,
                                                        'tt_veg': None,
                                                        'tt_rep': None,
                                                        'gamma_1': 0.027,
                                                        'gamma_2': 0.0045,
                                                        'gamma_3': 0.0004,
                                                        'gamma_4_senes': 6,
                                                        'gamma_5_harvest': 0.5,
                                                        'cL3': 13000},
                                            'height': None,
                                            'cosA': 0.5,
                                            'Lm': 0.02,
                                            'Y': 6.0,
                                            'PID': 40}],
                            'height_method': 'carbon',
                            'dvi_method': 'THERMAL_TIME',
                            'layer_height_frac': [0.25, 0.25, 0.25, 0.25],
                            'LAI_method': 'carbon',
                            'LAI': None,
                            'SAI_method': 'estimate total',
                            'SAI': None,
                            'LAI_distribution_method': 'fraction',
                            'fLAI': [[0.25], [0.25], [0.25], [0.25]],
                            'max_lai_per_layer': None,
                            'leaf_emergence_multiplier': 1,
                            'phenology_options': {'flag_leaf_only': False,
                                                  'phenology_method': 'season_fraction',
                                                  'dvi_method': 'disabled',
                                                  'LAI_method': 'estimate total',
                                                  'time_type': 'thermal_time',
                                                  'sgs_time_type': 'julian_day',
                                                  'sgs_key_day': 'sowing_day',
                                                  'zero_day': 'sowing',
                                                  'plant_emerge_method': 'constant',
                                                  'flag_leaf_emerge_method': 'constant',
                                                  'use_vernalisation': True,
                                                  'use_photoperiod_factor': True,
                                                  'sowing_day_method': 'INPUT',
                                                  'latitude': None},
                            'ozone_deposition_method': 'multi layer'},
             'Met': {'td_base_temperature': 0,
                     'thermal_time_start': 318,
                     'thermal_time_offset': 0,
                     'thermal_time_method': 'HOURLY',
                     'dd_calc_method': None,
                     'PARsunshade_method': 'FARQUHAR1997',
                     'inputs': {'time_method': 'skip',
                                'row_index_method': 'calculated',
                                'dom_method': 'skip',
                                'mm_method': 'skip',
                                'year_method': 'skip',
                                'dd_method': 'input',
                                'dd_required': True,
                                'hr_method': 'input',
                                'hr_required': True,
                                'CO2_method': 'constant',
                                'CO2_constant': 391.0,
                                'CO2_fillna': None,
                                'CO2_required': True,
                                'O3_method': 'input',
                                'O3_constant': None,
                                'O3_fillna': None,
                                'O3_required': True,
                                'Ts_C_method': 'input',
                                'Ts_C_constant': None,
                                'Ts_C_fillna': None,
                                'Ts_C_required': True,
                                'Ts_K_method': 'skip',
                                'Ts_K_constant': None,
                                'Ts_K_fillna': None,
                                'Ts_K_required': False,
                                'P_method': 'input',
                                'P_constant': None,
                                'P_fillna': None,
                                'P_required': True,
                                'precip_method': 'input',
                                'precip_constant': None,
                                'precip_fillna': None,
                                'precip_required': True,
                                'u_method': 'input',
                                'u_constant': None,
                                'u_fillna': None,
                                'u_required': True,
                                'uh_method': 'skip',
                                'uh_constant': None,
                                'uh_fillna': None,
                                'uh_required': False,
                                'O3_nmol_method': 'calculated',
                                'O3_nmol_constant': None,
                                'O3_nmol_fillna': None,
                                'O3_nmol_required': False,
                                'Tleaf_C_method': 'skip',
                                'Tleaf_C_constant': None,
                                'Tleaf_C_fillna': None,
                                'Tleaf_C_required': False,
                                'u__method': 'skip',
                                'u__constant': None,
                                'u__fillna': None,
                                'u__required': False,
                                'Rn_method': 'calculated',
                                'Rn_constant': None,
                                'Rn_fillna': None,
                                'Rn_required': False,
                                'R_method': 'calculated',
                                'R_constant': None,
                                'R_fillna': None,
                                'R_required': False,
                                'PAR_method': 'calculated',
                                'PAR_constant': None,
                                'PAR_fillna': None,
                                'PAR_required': True,
                                'PPFD_method': 'input',
                                'PPFD_constant': None,
                                'PPFD_fillna': None,
                                'PPFD_required': False,
                                'Idrctt_method': 'calculated',
                                'Idrctt_constant': None,
                                'Idrctt_fillna': None,
                                'Idrctt_required': False,
                                'Idfuse_method': 'calculated',
                                'Idfuse_constant': None,
                                'Idfuse_fillna': None,
                                'Idfuse_required': False,
                                'VPD_method': 'calculated',
                                'VPD_constant': None,
                                'VPD_fillna': None,
                                'VPD_required': True,
                                'RH_method': 'input',
                                'RH_constant': None,
                                'RH_fillna': None,
                                'RH_required': False,
                                'h_method': 'skip',
                                'h_constant': None,
                                'h_fillna': None,
                                'h_required': False,
                                'SWP_method': 'skip',
                                'SWP_constant': None,
                                'SWP_fillna': None,
                                'SWP_required': False,
                                'SWC_method': 'skip',
                                'SWC_constant': None,
                                'SWC_fillna': None,
                                'SWC_required': False,
                                'VPD_dd_method': 'calculated',
                                'VPD_dd_constant': None,
                                'VPD_dd_fillna': None,
                                'VPD_dd_required': False,
                                'esat_method': 'calculated',
                                'esat_constant': None,
                                'esat_fillna': None,
                                'esat_required': False,
                                'eact_method': 'calculated',
                                'eact_constant': None,
                                'eact_fillna': None,
                                'eact_required': False,
                                'td_method': 'skip',
                                'td_constant': None,
                                'td_fillna': None,
                                'td_required': False,
                                'is_daylight_method': 'calculated',
                                'is_daylight_constant': None,
                                'is_daylight_fillna': None,
                                'is_daylight_required': False,
                                'sinB_method': 'calculated',
                                'sinB_constant': None,
                                'sinB_fillna': None,
                                'sinB_required': True,
                                'Hd_method': 'skip',
                                'Hd_constant': None,
                                'Hd_fillna': None,
                                'Hd_required': False,
                                'leaf_fphen_method': 'skip',
                                'leaf_fphen_constant': None,
                                'leaf_fphen_fillna': None,
                                'leaf_fphen_required': False,
                                'fphen_method': 'skip',
                                'fphen_constant': None,
                                'fphen_fillna': None,
                                'fphen_required': False,
                                'LAI_method': 'skip',
                                'LAI_constant': None,
                                'LAI_fillna': None,
                                'LAI_required': False,
                                'V_cmax_25_method': 'skip',
                                'V_cmax_25_constant': None,
                                'V_cmax_25_fillna': None,
                                'V_cmax_25_required': False,
                                'J_max_25_method': 'skip',
                                'J_max_25_constant': None,
                                'J_max_25_fillna': None,
                                'J_max_25_required': False,
                                'snow_depth_method': 'skip',
                                'snow_depth_constant': None,
                                'snow_depth_fillna': None,
                                'snow_depth_required': False,
                                'cloudfrac_method': 'skip',
                                'cloudfrac_constant': None,
                                'cloudfrac_fillna': None,
                                'cloudfrac_required': False,
                                'ustar_ref_method': 'skip',
                                'ustar_ref_constant': None,
                                'ustar_ref_fillna': None,
                                'ustar_ref_required': False,
                                'ustar_method': 'skip',
                                'ustar_constant': None,
                                'ustar_fillna': None,
                                'ustar_required': False},
                     'sparse_data': False},
             'soil_moisture': {'soil_texture': 'loam',
                               'soil_config': {'b': 6.58,
                                               'FC': 0.29,
                                               'SWP_AE': -0.00188,
                                               'Ksat': 0.0002286},
                               'root': 0.4,
                               'PWP': -4.0,
                               'ASW_FC': 0.06607020548895037,
                               'source': 'disabled',
                               'initial_SWC': None,
                               'run_off_fraction': 0.0,
                               'MAD': 0.0},
             'resistance': {'ra_calc_method': 'simple', 'rsur_calc_method': 'multi_layer'},
             'carbon_allocation': {'use_carbon_allocation': True,
                                   'a_root': 18.4,
                                   'a_stem': 16.8,
                                   'a_leaf': 18.4,
                                   'b_root': -20.9,
                                   'b_stem': -14.5,
                                   'b_leaf': -18.11,
                                   'gamma': 14,
                                   'delta': -0.0507,
                                   'theta': 0.5,
                                   'k': 1.4,
                                   'lambdav': 0.4,
                                   'f_green_leaf': 0.95,
                                   'f_brown_leaf': 0.24,
                                   'dry_to_wet_biomass': 1.1904761904761905,
                                   'grain_to_ear': 0.85},
             'output': {'fields': ['dd',
                                   'dd_e',
                                   'hr',
                                   'ts_c',
                                   'par',
                                   'td',
                                   'td_v',
                                   'photoperiod_factor',
                                   'Vf',
                                   'V_acc',
                                   'V_pos',
                                   'V_neg',
                                   'canopy_lai',
                                   'canopy_lai_brown',
                                   'canopy_sai',
                                   'lai',
                                   'lai_brown',
                                   'dvi',
                                   'photoperiod',
                                   'o3_ppb_i',
                                   'canopy_vd',
                                   'u_i',
                                   'Tleaf_C',
                                   'ustar',
                                   'ustar_ref',
                                   'canopy_height',
                                   'micro_u',
                                   'micro_O3',
                                   'PARsun',
                                   'PARshade',
                                   'o3_ppb',
                                   'o3_nmol_m3',
                                   'layer_height',
                                   'LAI_flag',
                                   'A_n',
                                   'A_n_sunlit',
                                   'A_n_limit_factor',
                                   'fst',
                                   'fst_sun',
                                   'fst_canopy',
                                   'fst_acc',
                                   'fst_acc_day',
                                   'rext',
                                   'rsto_l',
                                   'rb_l',
                                   'gsto_l',
                                   'gsto_l_sunlit',
                                   'gsto_l_bulk',
                                   'gsto',
                                   'gsto_bulk',
                                   'gsto_canopy',
                                   'A_n_canopy',
                                   'c_root',
                                   'c_stem',
                                   'c_leaf',
                                   'c_lbrn',
                                   'c_harv',
                                   'c_resv',
                                   'p_root',
                                   'p_stem',
                                   'p_leaf',
                                   'p_harv',
                                   'stem_dm',
                                   'leaf_dm',
                                   'lbrn_dm',
                                   'total_leaf_dm',
                                   'straw_dm',
                                   'ear_dm',
                                   'aboveground_dm',
                                   'belowground_dm',
                                   'grain_dm',
                                   'harvest_index',
                                   'yield_ha',
                                   'gpp',
                                   'npp',
                                   'npp_acc',
                                   'R_pm',
                                   'R_pg',
                                   'fO3_h',
                                   'fO3_d',
                                   'fO3_l',
                                   'f_LS',
                                   'f_LA',
                                   'c_i',
                                   'td_dd',
                                   'td_dd_flag',
                                   'pody',
                                   'pody_sun',
                                   'pod0',
                                   'precip_acc',
                                   'swp',
                                   'asw',
                                   'smd',
                                   'sn',
                                   'ei',
                                   'et',
                                   'pet',
                                   'es',
                                   'ei_acc',
                                   'eat_acc',
                                   'et_acc',
                                   'pet_acc',
                                   'es_acc',
                                   'f_phen',
                                   'leaf_f_phen',
                                   'f_light',
                                   'leaf_f_light',
                                   'f_temp',
                                   'f_VPD',
                                   'f_SW',
                                   'f_O3',
                                   'rsto_c',
                                   'ra',
                                   'rb',
                                   'rsur',
                                   'rinc',
                                   'rsto_h2o',
                                   'V_cmax_25',
                                   'J_max_25',
                                   'LAIsunfrac',
                                   'component_LAI',
                                   'V_cmax',
                                   'J_max',
                                   'R_d',
                                   'R_dc',
                                   'total_emerged_leaves',
                                   'leaf_phenology_stage',
                                   'leaf_pop_distribution',
                                   'phenology_stage',
                                   'growing_populations',
                                   'layer_lai',
                                   'layer_lai_brown',
                                   'fLAI',
                                   't_eff'],
                        'log_multilayer': True}}
        k_out = find_key(d, k)
        assert k_out == "Land_Cover.parameters.0.pn_gsto.t_b"


class TestFindAllKeys:

    def test_find_all_keys(self):
        k = "foo"
        d = {
            "bar": {
                "foo": 2,
                "roo": 3,
                "ree": {
                    "foo": 4,
                    "sow": 5,
                }
            }
        }
        k_out = find_all_keys(d, k)
        assert len(k_out) == 2
        assert k_out[0] == "bar.foo"
        assert k_out[1] == "bar.ree.foo"

    def test_find_all_keys_in_list(self):
        k = "foo"
        d = {
            "bar": [{
                "foo": 2,
                "roo": 3,
                "ree": {
                    "foo": 4,
                    "sow": 5,
                }
            }, {
                "foo": 2,
                "roo": 3,
                "ree": {
                    "foo": 4,
                    "sow": 5,
                }
            }]
        }
        k_out = find_all_keys(d, k)
        assert len(k_out) == 4
        assert k_out[0] == "bar.0.foo"
        assert k_out[1] == "bar.0.ree.foo"
        assert k_out[2] == "bar.1.foo"
        assert k_out[3] == "bar.1.ree.foo"
