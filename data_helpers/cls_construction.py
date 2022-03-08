"""Various functions for generating classes from lower level data structures such as json."""
from dataclasses import asdict, dataclass, field, make_dataclass
import json
from enum import Enum
from typing import Callable, List, Tuple, Union
from data_helpers.encoders import AdvancedJsonEncoder



@dataclass
class FieldBase:

    variable: str
    label: str
    cls: type
    desc: str = ''
    required: bool = False
    default: Callable[[], any] = None
    unit: any = None

    def __asdict__(self):
        out = asdict(self)
        if out.get('default', None):
            out['default'] = self.default()
        return out


@dataclass
class Group:

    variable: str
    label: str
    required: bool
    fields: List[FieldBase]
    default: Callable[[], any] = None
    desc: str = ''

    def __asdict__(self):
        out = asdict(self)
        if out.get('default', None):
            # TODO: May not be correct default here
            out['default'] = self.default()
        out['fields'] = [f.__asdict__() for f in self.fields]
        out['type'] = 'group'
        return out

def group_to_json(group: Group, **kwargs) -> str:
    return json.dumps(group, cls=AdvancedJsonEncoder , **kwargs)


@dataclass
class ListBase:

    field: Union[FieldBase, Group]
    default: Callable[[], any] = None
    default_size: int = 0


    def __asdict__(self):
        out = asdict(self)
        if out.get('default', None):
            out['default'] = self.default()
        # TODO: Should we store field type here?
        out['type'] = "List"
        return out

    def __post_init__(self):
        # TODO: Might need to patch dataclass attrs here

        # Name the list variable to match the sub object variable.
        setattr(self, 'variable', self.field.variable)
        self.variable = self.field.variable


@dataclass
class Field(FieldBase):
    dependencies: List[str] = field(default_factory=lambda: [])

@dataclass
class NumberField(FieldBase):
    dependencies: List[str] = field(default_factory=lambda: [])
    min: float = 0
    max: float = 100
    step: float = 1.0


@dataclass
class Option:

    uid: str
    label: str
    description: str = ''
    dependencies: List[str] = field(default_factory=lambda: [])  # parameters required by option


@dataclass
class ListField(ListBase):

    pass


@dataclass
class ListGroup(ListBase):

    pass


@dataclass
class Select(FieldBase):

    options: List[Tuple[str, str]] = field(default_factory=lambda: [])
    required_params: List[str] = field(default_factory=lambda: [])

    def __asdict__(self):
        out = asdict(self)
        if out.get('default', None):
            # TODO: May not be correct default here
            out['default'] = self.default()
        return out


def generate_enum_from_select(f: Select):
    return Enum(f"{f.variable.capitalize()}Enum", dict([(opt.label, opt.uid) for opt in f.options]))


def label_to_cls_name(label):
    return ''.join(map(lambda s: s.capitalize(), label.split(' ')))


def get_field_cls(f: FieldBase, module):
    subclasses = {}
    if isinstance(f, Group):
        # TODO: Return subclasses
        Cls, subclasses = group_to_class(f, module)
    elif isinstance(f, Field):
        Cls = f.cls
    elif isinstance(f, NumberField):
        Cls = f.cls
    elif isinstance(f, Select):
        Cls = generate_enum_from_select(f)
    else:
        raise ValueError(f"Invalid fieldtype: {type(f)}")
    return Cls, subclasses


def get_field_default(f: FieldBase, Cls):
    def_value = None
    use_def = getattr(f, 'default', None) is not None or not getattr(f, 'required', False)
    if isinstance(f, Group):
        pass
    elif isinstance(f, ListField):
        if f.field.default is not None:
            def_value = field(default_factory=lambda: f.field.default)
    elif isinstance(f, ListGroup):
        def_value = field(default_factory=lambda: Cls())
    elif isinstance(f, Field):
        if f.default is not None:
            if type(f.cls) in [dict, list]:
                def_value = field(default_factory=f.default)
            else:
                def_value = field(default=f.default)
    elif isinstance(f, NumberField):
        if f.default is not None:
            if type(f.cls) in [dict, list]:
                def_value = field(default_factory=lambda: f.default)
            else:
                def_value = field(default=f.default)
    elif isinstance(f, Select):
        # TODO: Set default
        if f.default is not None:
            def_value = field(default=Cls[f.default()])
    else:
        raise ValueError(f"Invalid fieldtype: {type(f)}")
    return use_def, def_value


def field_to_dataclass_field(f: Union[FieldBase, ListBase], module):
    """Get Class and Subclasses from field schema.

    Parameters
    ----------
    f : Union[FieldBase, ListBase]
        The field schema
    module : _type_
        Module to link to

    Returns
    -------
    Tuple[str, SubClasses]
        Name and generated classes
    """
    if isinstance(f, ListBase):
        Cls, subclasses = get_field_cls(f.field, module)
        use_def = not getattr(f.field, 'required', False)
        def_value = True, field(default_factory=lambda: []) if use_def else None
        field_name = f.field.variable
        field_out = (field_name, Cls) if not use_def else (field_name, Cls, def_value)
        classes = [*subclasses.items(), (label_to_cls_name(f.field.label), Cls)]
        return field_out, classes
    else:
        Cls, subclasses = get_field_cls(f, module)
        use_def, def_value = get_field_default(f, Cls)
        field_name = f.variable
        field_out = (field_name, Cls) if not use_def else (field_name, Cls, def_value)
        classes = [*subclasses.items(), (label_to_cls_name(f.label), Cls)]
        return field_out, classes


def sort_fields(f: Field) -> bool:
    """Sort dataclass construction fields.

    Makes fields with default arg occur after fields without default arg.
    To avoid error: `non-default argument 'sel' follows default argument`
    """

    if isinstance(f, ListBase):
        use_def = not getattr(f.field, 'required', False)
        return 1 if use_def else 0
    use_def = getattr(f, 'default', None) is not None or not getattr(f, 'required', False)
    return 1 if use_def else 0


def get_val_default(k: FieldBase) -> any:
    try:
        return k.default() if k.default is not None else None
    except TypeError as e:
        if "object is not callable" in str(e):
            raise TypeError(f"Default value for {k.label or k.variable} must be a function")
        else:
            raise e


def create_with_default(group: Group, Cls, subclasses):
    def inner(input_data: dict = None):
        _input_data = input_data or {}
        args = {}
        for k in group.fields:
            input_val = _input_data.get(k.variable, None)
            if isinstance(k, Group):
                key = label_to_cls_name(k.label)
                args[k.variable] = subclasses[key]._default(input_val)
            elif isinstance(k, ListGroup):
                if input_val is not None:
                    raise NotImplementedError("Input Lists not implemented")
                if k.default_size:
                    key = label_to_cls_name(k.field.label)
                    args[k.variable] = [subclasses[key]._default() for _ in range(k.default_size)]
                else:
                    args[k.variable] = k.default() if k.default is not None else []
            elif isinstance(k, ListField):
                if input_val is not None:
                    assert type(input_val) == type([]), f"Must provide list for {k.variable}"
                    args[k.variable] = input_val
                else:
                    if k.default_size:
                        field_default = k.field.default() if k.field.default is not None else None
                        args[k.variable] = [field_default for _ in range(k.default_size)]
                    else:
                        args[k.variable] = k.default() if k.default is not None else []

            elif isinstance(k, Select):
                key = label_to_cls_name(k.label)
                if k.default is not None:
                    default_val = get_val_default(k)
                    args[k.variable] = subclasses[key][default_val]
                else:
                    args[k.variable] = None
            elif isinstance(k, (Field, NumberField)):
                if input_val:
                    args[k.variable] = input_val
                else:
                    args[k.variable] = get_val_default(k)

            else:
                raise TypeError(f"Default setup not implemented for {type(k)}")

        return Cls(**args)
    return inner


def group_to_class(group: Group, module) -> object:
    sorted_fields = sorted(group.fields, key=sort_fields)
    fields_parsed, subclasses = zip(*[field_to_dataclass_field(f, module)
                                   for f in sorted_fields])
    #    classes is a List[List[Tuple[str, Cls]]]
    subclasses_dict = dict([b for a in subclasses for b in a])
    obj = make_dataclass(label_to_cls_name(group.label), fields_parsed)
    obj.__doc__ = f"{group.label} Generated Dataclass"
    obj.__module__ = module
    obj._default = create_with_default(group, obj, subclasses_dict)
    return obj, subclasses_dict


class Struct(object):
    """Create a class from a dictionary structure."""

    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value


try:
    import ipywidgets as widgets

    class ConfigGeneratorUI():

        def __init__(self, group: Group) -> None:
            self.group = group
            self.fields = group.fields
            self.field_widgets = {}
            self.field_inputs = {}

            self.input_layout = lambda: widgets.Layout(width='40%')
            self.label_layout = widgets.Layout(
                width='20%',
                display="flex",
                justify_content="flex-end",
                padding="1px",
            )
            self.desc_layout = widgets.Layout(
                width='40%',
                display="flex wrap",
                justify_content="flex-start",
            )
            self.field_container_layout = widgets.Layout(
                display='flex',
                width='100%',
                align_items='stretch',
                flex_flow='horiz',
                padding="1px",
            )

            self.container_layout = widgets.Layout(
                display='flex',
                width='100%',
                flex_flow='column',
                align_items='stretch',
            )

        def collapsable_container_wrap_layout(self, expanded=True): return widgets.Layout(
            display='flex',
            width='100%',
            border='solid 0.1px grey',
            flex_flow='column',
            align_items='stretch',
            max_height='10000px',
            height='100%',
            visibility='visible',
            padding="10px",
        ) if expanded else widgets.Layout(
            display='flex',
            width='100%',
            border='solid 0.1px grey',
            flex_flow='column',
            align_items='stretch',
            max_height='0px',
            visibility='hidden',
            padding="10px",
        )

        def get_field(self, field: FieldBase):
            if isinstance(field, Select):
                return widgets.RadioButtons(
                    options=[(opt.label, opt.uid) for opt in field.options],
                    layout=self.input_layout(),
                    disabled=False
                )
            if isinstance(field, NumberField):
                if field.cls == int:
                    return widgets.IntSlider(layout=self.input_layout(), min=field.min, max=field.max, step=field.step)

            if field.cls == str:
                return widgets.Text(layout=self.input_layout())
            return widgets.Text(layout=self.input_layout())

        def get_field_widget_wrap(self, f, label, description):
            input_field = self.get_field(f)
            contained = widgets.Box([label, input_field, description],
                                    layout=self.field_container_layout)
            return input_field, contained

        def get_group_widget(self, f, label, description):
            input_field, field_widgets, field_inputs = self.get_widget_container_from_group(f)
            return field_inputs, input_field

        def get_list_widget(self, f, label, description):
            MAX_LIST_LENGTH = 3
            def item_layout(): return widgets.Layout(visibility='hidden', max_height='0px')

            field_widgets, field_inputs = zip(
                *[self.get_widget_container(f.field) for _ in range(MAX_LIST_LENGTH)])

            field_widgets_wrapped = [widgets.Box([w], layout=item_layout()) for w in field_widgets]
            box_layout = widgets.Layout(
                # overflow='hidden scroll',
                border='1px solid green',
                width='100%',
                # max_height='100px', # TODO: This causes squashed inputs
                flex_flow='column',
                display='flex',
                padding="10px",
            )

            field_count = widgets.IntSlider(value=0, min=0, max=len(
                field_widgets_wrapped), description="Field count")

            def limit_inputs_to_slider(sender):
                for i, inputItem in enumerate(field_widgets_wrapped):
                    if i >= field_count.value:
                        inputItem.layout.visibility = "hidden"
                        inputItem.layout.max_height = "0px"
                    else:
                        inputItem.layout.visibility = "visible"
                        inputItem.layout.max_height = "10000px"

            field_count.observe(limit_inputs_to_slider, names="value")

            inputs_contained = widgets.Box(field_widgets_wrapped, layout=box_layout)
            list_label = widgets.HTML(f"LIST: {f.field.variable}", layout=self.label_layout)
            list_label.add_class("list_label")

            contained_a = widgets.Box([list_label, field_count, description],
                                      layout=self.field_container_layout)
            contained = widgets.VBox([contained_a, inputs_contained])
            return (field_count, field_inputs), contained

        def get_widget_container(self, f):
            is_list = isinstance(f, ListBase)
            label = widgets.HTML(f.field.label if is_list else f.label,
                                 layout=self.label_layout)
            label.add_class("field_label")
            desc = widgets.HTML(f.field.desc if is_list else f.desc, layout=self.desc_layout)

            if is_list:
                input_field, contained = self.get_list_widget(f, label, desc)
            else:
                get_widget = self.get_group_widget if isinstance(
                    f, Group) else self.get_field_widget_wrap
                input_field, contained = get_widget(f, label, desc)
            return contained, input_field

        def get_widget_container_from_group(self, group):
            field_widgets = []
            field_inputs = []
            for i, f in enumerate(group.fields):
                contained, input_field = self.get_widget_container(f)

                field_widgets.append(contained)
                field_inputs.append((i, input_field))

            sections = []
            content = widgets.Box(
                field_widgets, layout=self.collapsable_container_wrap_layout(False))
            header_btn = widgets.Button(description=group.label)
            sections.append(widgets.Box([header_btn, content], layout=self.container_layout))

            def on_button_clicked(target):
                def inner(b):
                    is_visable = target.layout.visibility != 'hidden'
                    target.layout = self.collapsable_container_wrap_layout(
                        False) if is_visable else self.collapsable_container_wrap_layout(True)
                return inner
            header_btn.on_click(on_button_clicked(content))
            container = widgets.VBox(sections, layout=self.field_container_layout)
            return container, field_widgets, field_inputs

        def generate_widgets(self):
            # TODO: Get layouts from class init
            container, field_widgets, field_inputs = self.get_widget_container_from_group(
                self.group)
            self.field_widgets = field_widgets
            self.field_inputs = field_inputs
            return container

        def get_field_data(self, f, w):
            if isinstance(f, FieldBase):
                return w.value
            if isinstance(f, Group):
                return {
                    fi.variable if not isinstance(fi, ListBase) else fi.field.variable:
                    self.get_field_data(fi, wi[1])
                    for fi, wi in zip(f.fields, w)}
            if isinstance(f, ListBase):
                # TODO: Limit this to range of IntSlider
                return [self.get_field_data(f.field, wi) for wi in w[1]][0:w[0].value]
            return 'UNDEFINED'

        def get_data_dict(self):
            out = {}
            for (i, w) in self.field_inputs:
                f = self.fields[i]
                out[f.variable if not isinstance(
                    f, ListBase) else f.field.variable] = self.get_field_data(f, w)
            return out

except ImportError or ModuleNotFoundError:
    pass
