# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestGroupToJson.test_can_dump_group_to_json[InnerGroupStructure-obj1] out.json'] = '''{
  "_parentcls": "<class \'data_helpers.cls_construction.Group\'>",
  "default": null,
  "desc": "",
  "fields": [
    {
      "cls": "<class \'str\'>",
      "default": "default_name",
      "dependencies": [],
      "desc": "Name",
      "label": "Name",
      "required": true,
      "unit": null,
      "variable": "name"
    }
  ],
  "label": "Inner Group",
  "required": true,
  "type": "group",
  "variable": "inner_group"
}'''

snapshots['TestGroupToJson.test_can_dump_group_to_json[example_field-obj0] out.json'] = '''{
  "_parentcls": "<class \'data_helpers.cls_construction.Field\'>",
  "cls": "<class \'str\'>",
  "default": "default_name",
  "dependencies": [],
  "desc": "Name",
  "label": "Name",
  "required": true,
  "unit": null,
  "variable": "name"
}'''

snapshots['TestGroupToJson.test_can_dump_group_to_json[example_group-obj2] out.json'] = '''{
  "_parentcls": "<class \'data_helpers.cls_construction.Group\'>",
  "default": null,
  "desc": "",
  "fields": [
    {
      "cls": "<class \'str\'>",
      "default": null,
      "dependencies": [],
      "desc": "Example field description a",
      "label": "Foo",
      "required": true,
      "unit": null,
      "variable": "foo"
    },
    {
      "cls": "<class \'str\'>",
      "default": "A",
      "desc": "Example field",
      "label": "Sel",
      "options": [
        {
          "dependencies": [],
          "description": [],
          "label": "A",
          "uid": "a"
        },
        {
          "dependencies": [],
          "description": [],
          "label": "B",
          "uid": "b"
        }
      ],
      "required": true,
      "required_params": [],
      "unit": null,
      "variable": "sel"
    },
    {
      "cls": "<class \'int\'>",
      "default": 9,
      "dependencies": [],
      "desc": "Example number field",
      "label": "Bar",
      "max": 33,
      "min": 3,
      "required": true,
      "step": 3,
      "unit": null,
      "variable": "bar"
    },
    {
      "default": null,
      "default_size": 0,
      "field": {
        "cls": "<class \'int\'>",
        "default": "PLACEHOLDER_FUNC",
        "dependencies": [],
        "desc": "Example list",
        "label": "Foos",
        "required": false,
        "unit": null,
        "variable": "foos"
      },
      "type": "List"
    },
    {
      "default": null,
      "desc": "",
      "fields": [
        {
          "cls": "<class \'str\'>",
          "default": null,
          "dependencies": [],
          "desc": "",
          "label": "Inner",
          "required": false,
          "unit": null,
          "variable": "inner"
        }
      ],
      "label": "Main",
      "required": true,
      "type": "group",
      "variable": "main"
    },
    {
      "default": null,
      "desc": "",
      "fields": [
        {
          "cls": "<class \'str\'>",
          "default": null,
          "dependencies": [],
          "desc": "",
          "label": "InnerB",
          "required": false,
          "unit": null,
          "variable": "inner_b"
        }
      ],
      "label": "Other",
      "required": true,
      "type": "group",
      "variable": "other"
    },
    {
      "default": null,
      "desc": "",
      "fields": [
        {
          "default": null,
          "desc": "",
          "fields": [
            {
              "cls": "<class \'str\'>",
              "default": "default_name",
              "dependencies": [],
              "desc": "Name",
              "label": "Name",
              "required": true,
              "unit": null,
              "variable": "name"
            }
          ],
          "label": "Inner Group",
          "required": true,
          "type": "group",
          "variable": "inner_group"
        }
      ],
      "label": "Outer",
      "required": true,
      "type": "group",
      "variable": "outer"
    },
    {
      "default": null,
      "default_size": 0,
      "field": {
        "default": null,
        "desc": "",
        "fields": [
          {
            "cls": "<class \'str\'>",
            "default": null,
            "dependencies": [],
            "desc": "",
            "label": "Inner List Field",
            "required": false,
            "unit": null,
            "variable": "inner_l"
          }
        ],
        "label": "List Group Example",
        "required": true,
        "variable": "list_group"
      },
      "type": "List"
    },
    {
      "default": null,
      "desc": "",
      "fields": [
        {
          "default": null,
          "default_size": 0,
          "field": {
            "default": null,
            "desc": "",
            "fields": [
              {
                "cls": "<class \'str\'>",
                "default": null,
                "dependencies": [],
                "desc": "",
                "label": "Foo",
                "required": false,
                "unit": null,
                "variable": "foo"
              }
            ],
            "label": "b",
            "required": true,
            "variable": "b"
          },
          "type": "List"
        }
      ],
      "label": "A",
      "required": true,
      "type": "group",
      "variable": "a"
    }
  ],
  "label": "Generated Type",
  "required": true,
  "type": "group",
  "variable": "GeneratedType"
}'''
