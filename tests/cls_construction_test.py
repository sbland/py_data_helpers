from dataclasses import is_dataclass
import inspect
from typing import get_args
from data_helpers.cls_parsing import is_enum, is_iterable
import pytest
from enum import Enum
from data_helpers.cls_construction import *


example_fields = [
    Field('foo', 'Foo', str, 'Example field description a', True),
    Select(
        'sel', 'Sel', str, 'Example field', True,
        default='A',
        options=[
               Option('a', 'A', []),
               Option('b', 'B', [])
        ]
    ),

    NumberField('bar', 'Bar', int, 'Example number field', True, 9, min=3, max=33, step=3),
    ListField(Field('foos', 'Foos', int, 'Example list', default=[])),
    Group('main', 'Main', True, [
        Field('inner', 'Inner', str),
    ]),
    Group('other', 'Other', True, [
        Field('inner_b', 'InnerB', str),
    ]),
    ListGroup(Group('list_group', 'List Group Example', True, [
        Field('inner_l', 'Inner List Field', str),
    ])),
]

example_group = Group('GeneratedType', 'Generated Type', True, example_fields)


class SelEnum(Enum):
    A = 'a'
    B = 'b'


@dataclass
class MainGroup:

    inner: str


@dataclass
class OtherGroup:

    inner_b: str


@dataclass
class ListGroupExample:

    inner_l: str


@dataclass
class GeneratedType:
    foo: str
    sel: SelEnum
    bar: int = 9
    foos: List[int] = field(default_factory=lambda: [])
    main: MainGroup = field(default_factory=lambda: MainGroup())
    other: OtherGroup = field(default_factory=lambda: OtherGroup())
    list_group: List[ListGroupExample] = field(default_factory=lambda: [])


def check_class_match(cls_a, cls_b, verbose=False) -> bool:
    try:
        match_attrs = ['__class__', '__dataclass_params__', '__delattr__', '__dir__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__',
                       '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__setattr__', '__sizeof__', '__str__', '__weakref__']
        a_members = dict(inspect.getmembers(cls_a))
        b_members = dict(inspect.getmembers(cls_b))

        for k in a_members.keys():
            assert k in b_members
        for k in match_attrs:
            assert str(a_members[k]) == str(b_members[k])

        for k in a_members['__annotations__'].keys():
            # Assert root has all groups
            assert k in b_members['__annotations__']
            print(f"check sub objs {k}")

            a_cls = a_members['__annotations__'][k]
            b_cls = b_members['__annotations__'][k]

            a_cls = a_cls if not is_iterable(a_cls) else get_args(a_cls)[0]
            b_cls = b_cls if not is_iterable(b_cls) else get_args(b_cls)[0]

            if a_cls != b_cls:
                if is_dataclass(a_cls):
                    a_field_members = dict(inspect.getmembers(
                        a_cls))
                    b_field_members = dict(inspect.getmembers(
                        b_cls))
                    for f in a_field_members['__annotations__'].keys():
                        assert str(a_field_members['__annotations__'][f]) \
                            == str(b_field_members['__annotations__'][f])
                elif is_enum(a_cls):
                    assert [a.value for a in a_cls] == [a.value for a in b_cls]
                    assert [a.name for a in a_cls] == [a.name for a in b_cls]
                else:
                    print(type(a_cls))
                    raise ValueError("Invalid type")
        # TODO: Check enums match

        # Does not match because import location is different
        # assert expected_members["__doc__"] == out_members["__doc__"]

    except AssertionError as e:
        if verbose:
            raise e
        else:
            return False
    return True


class TestConstructDataclassFromDict:

    def test_should_be_able_to_construct_cls_from_fields(self):
        received, subclasses = group_to_class(example_group, globals().get('__name__'))
        assert type(received) == type(GeneratedType)

        assert check_class_match(GeneratedType, received, True)

    def test_should_return_subclasses(self):
        OutCls, subclasses = group_to_class(example_group, globals().get('__name__'))
        assert type(subclasses["Main"]) == type(MainGroup)
        assert type(subclasses["Other"]) == type(MainGroup)

    def test_should_be_able_to_create_sub_objs(self):
        OutCls, subclasses = group_to_class(example_group, globals().get('__name__'))
        MainGroupGenerated = subclasses["Main"]
        # Note args are not type checked
        mainGroup = MainGroupGenerated("hello")
        assert mainGroup.inner == "hello"

    def test_should_be_able_to_create_instance_of_class(self):
        OutCls, subclasses = group_to_class(example_group, globals().get('__name__'))
        MainGroupGenerated = subclasses["Main"]
        mainGroup = MainGroupGenerated("hello")
        OtherGroupGenerated = subclasses["Other"]
        otherGroup = OtherGroupGenerated("World")
        SelEnumGenerated = subclasses["Sel"]
        ListGroupExampleGenerated = subclasses["ListGroupExample"]

        assert mainGroup.inner == "hello"
        assert otherGroup.inner_b == "World"
        foo = "foo"
        sel = SelEnumGenerated.A
        out = OutCls(foo=foo, main=mainGroup, other=otherGroup, sel=sel,
                     list_group=ListGroupExampleGenerated('inner'))
        assert out.main.inner == "hello"
        assert out.other.inner_b == "World"
        assert out.sel.value == SelEnum.A.value

    def test_should_correctly_raise_missing_arg_error(self):
        OutCls, subclasses = group_to_class(example_group, globals().get('__name__'))

        with pytest.raises(TypeError) as e:
            out = OutCls()
        assert "TypeError(\"__init__() missing 4 required positional arguments: 'foo', 'main', 'other', and 'list_group'\")" in str(
            e)

    def test_should_parse_json_to_class_using_field_data(self):
        pass

    def test_should_be_able_to_create_a_list_field_with_length_tied_to_another_field(self):
        pass

    def test_should_set_default_field_to_none_if_not_required(self):
        pass


# class TestFieldToDataclassField:

#     @pytest.mark.parametrize('field target', )
#     def test_should_match_fields(self, field, target):
#         out = field_to_dataclass_field(field, globals().get("__name__"))
#         assert out == target


class TestConfigGeneratorUi:

    def test_can_create_ui_from_fields(self):
        config_ui = ConfigGeneratorUI(example_group)
        config_ui.generate_widgets()

    def test_can_get_input_data_from_generated_ui(self):
        config_ui = ConfigGeneratorUI(example_group)
        config_ui.generate_widgets()
        config_ui.field_inputs[3][1][0].value = 3
        config_ui.field_inputs[6][1][0].value = 3
        data = config_ui.get_data_dict()
        print(data)
        assert data == {
            'foo': '',
            'sel': 'a',
            'bar': 3,
            'foos': [
                '',
                '',
                '',
            ],
            'main': {
                'inner': '',
            },
            'other': {
                'inner_b': '',
            },
            'list_group': [
                {'inner_l': ''},
                {'inner_l': ''},
                {'inner_l': ''},
            ],
        }


# class TestStruct:

#     @pytest.fixture(autouse=True)
#     def _setup(self) -> None:
#         self.example_dict = {
#             "foo": "Foo",
#             "bar": {
#                 "a": 1,
#                 "b": 2,
#                 "c": 3,
#             }
#         }

#     def test_can_create_from_dictionary(self):
#         NewStruct = Struct(self.example_dict)
#         assert isinstance(NewStruct, # object)

#     def test_stores_variable_types(self):
#         NewStruct = Struct(self.example_dict)
#         print(dir(NewStruct))
#         assert NewStruct.__annotations__ == {}

#     # def test_can_create_instance_of_struct(self):
#     #     NewStruct = Struct(self.example_dict)
#     #     struct = NewStruct()
#     #     assert isinstance(struct, # NewStruct)

#     # def test_can_access_properties(self):
#     #     NewStruct = Struct(self.example_dict)
#     #     struct = NewStruct()
#     #     assert struct.foo == "bar"
