"""Various functions for generating classes from lower level data structures such as json."""
from dataclasses import asdict, dataclass, field, make_dataclass
from enum import Enum
from typing import List, Tuple


@dataclass
class FieldBase:

    variable: str
    label: str
    cls: type
    desc: str = ''
    required: bool = False
    default: any = None
    unit: any = None

    def __asdict__(self):
        return asdict(self)


@dataclass
class Group:

    variable: str
    label: str
    required: bool
    fields: List[FieldBase]


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
class ListWrap(Field):

    pass


@dataclass
class Select(FieldBase):

    options: List[Tuple[str, str]] = field(default_factory=lambda: [])
    required_params: List[str] = field(default_factory=lambda: [])


def generate_enum_from_select(f: Select):
    return Enum(f"{f.variable.capitalize()}Enum", dict([(opt.label, opt.uid) for opt in f.options]))


def field_to_dataclass_field(f: FieldBase, module):
    field_out = None
    Cls = None
    def_value = None
    use_def = getattr(f, 'default', None) is not None or not getattr(f, 'required', False)
    field_name = f.variable
    if isinstance(f, Group):
        # TODO: Return subclasses
        Cls, subclasses = group_to_class(f.label, f, module)
    elif isinstance(f, ListWrap):
        Cls = List[f.cls]
        if f.default is not None:
            def_value = field(default_factory=lambda: f.default)
    elif isinstance(f, Field):
        Cls = f.cls
        if f.default is not None:
            if type(f.cls) in [dict, list]:
                def_value = field(default_factory=lambda: f.default)
            else:
                def_value = field(default=f.default)
    elif isinstance(f, NumberField):
        Cls = f.cls
        if f.default is not None:
            if type(f.cls) in [dict, list]:
                def_value = field(default_factory=lambda: f.default)
            else:
                def_value = field(default=f.default)
    elif isinstance(f, Select):
        Cls = generate_enum_from_select(f)
        # TODO: Set default
        if f.default is not None:
            def_value = field(default=Cls[f.default])
    else:
        raise ValueError(f"Invalid fieldtype: {type(f)}")
    field_out = (field_name, Cls) if not use_def else (field_name, Cls, def_value)
    return field_out, (f.label, Cls)


def sort_fields(field: Field) -> bool:
    """Sort dataclass construction fields.

    Makes fields with default arg occur after fields without default arg.
    To avoid error: `non-default argument 'sel' follows default argument`
    """
    return 1 if getattr(field, 'default', None) is not None else 0


def group_to_class(cls_name, group: Group, module) -> object:
    sorted_fields = sorted(group.fields, key=sort_fields)
    fields_parsed, classes = zip(*[field_to_dataclass_field(f, module)
                                   for f in sorted_fields])
    subclasses = dict(classes)
    obj = make_dataclass(cls_name, fields_parsed)
    obj.__doc__ = f"{group.label} Generated Dataclass"
    obj.__module__ = module
    return obj, subclasses


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

    def get_field(field: FieldBase, input_layout: widgets.Layout):
        if isinstance(field, Select):
            return widgets.RadioButtons(
                options=[(opt.label, opt.uid) for opt in field.options],
                layout=input_layout,
                disabled=False
            )
        if isinstance(field, NumberField):
            if field.cls == int:
                return widgets.IntSlider(layout=input_layout, min=field.min, max=field.max, step=field.step)

        if field.cls == str:
            return widgets.Text(layout=input_layout)
        return widgets.Text(layout=input_layout)

    class ConfigGeneratorUI():

        def __init__(self, fields: List[FieldBase]) -> None:
            self.fields = fields

        def generate_widgets(self):
            # TODO: Get layouts from class init
            input_layout = widgets.Layout(width='40%')
            label_layout = widgets.Layout(width='30%', display="flex", justify_content="flex-end")
            desc_layout = widgets.Layout(width='30%', display="flex", justify_content="flex-start")
            field_container_layout = widgets.Layout(
                display='flex', width='100%', align_items='stretch', flex_flow='horiz')

            def container_layout(expanded=True): return widgets.Layout(
                display='flex',
                border='solid 0.1px',
                flex_flow='column',
                align_items='stretch',
                height='auto',
                visibility='visible',
            ) if expanded else widgets.Layout(
                display='flex',
                border='solid 0.1px',
                flex_flow='column',
                align_items='stretch',
                height='0',
                visibility='hidden',
            )

            self.field_widgets = {}
            self.field_inputs = {}
            for i, field in enumerate(self.fields):
                if field.group not in self.field_widgets:
                    self.field_widgets[field.group] = []
                    self.field_inputs[field.group] = []
                label = widgets.Label(field.label, layout=label_layout)
                input_field = get_field(field, input_layout)
                desc = widgets.Label(field.desc, layout=desc_layout)
                contained = widgets.Box([label, input_field, desc], layout=field_container_layout)
                self.field_widgets[field.group].append(contained)
                self.field_inputs[field.group].append((i, input_field))

            sections = []
            for k, v in self.field_widgets.items():
                content = widgets.Box(v, layout=container_layout(False))
                header_btn = widgets.Button(description=k)
                sections.append(widgets.Box([header_btn, content], layout=container_layout()))

                def on_button_clicked(target, k):
                    def inner(b):
                        is_visable = target.layout.visibility != 'hidden'
                        target.layout = container_layout(
                            False) if is_visable else container_layout(True)
                    return inner
                header_btn.on_click(on_button_clicked(content, k))
            boxes = widgets.VBox(sections, layout=container_layout())
            return boxes

        def get_data_dict(self):
            out = {}
            for group in self.field_inputs:
                out[group] = {}
                group_widgets = self.field_inputs[group]
                for (i, w) in group_widgets:
                    field = self.fields[i]
                    out[group][field.variable] = w.value
            return out

except ImportError or ModuleNotFoundError:
    pass
