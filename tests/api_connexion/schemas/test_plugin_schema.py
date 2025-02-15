# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from unittest.mock import MagicMock

from flask import Blueprint
from flask_appbuilder import BaseView

from airflow.api_connexion.schemas.plugin_schema import (
    PluginCollection,
    plugin_collection_schema,
    plugin_schema,
)
from airflow.plugins_manager import AirflowPlugin

from tests_common.test_utils.compat import BaseOperatorLink


def plugin_macro(): ...


class MockOperatorLink(BaseOperatorLink):
    name = "mock_operator_link"

    def get_link(self, operator, *, ti_key) -> str:
        return "mock_operator_link"


bp = Blueprint("mock_blueprint", __name__, url_prefix="/mock_blueprint")


class MockView(BaseView): ...


appbuilder_menu_items = {
    "name": "mock_plugin",
    "href": "https://example.com",
}

app = MagicMock()


class MockPlugin(AirflowPlugin):
    name = "mock_plugin"
    flask_blueprints = [bp]
    fastapi_apps = [{"app": app, "name": "App name", "url_prefix": "/some_prefix"}]
    appbuilder_views = [{"view": MockView()}]
    appbuilder_menu_items = [appbuilder_menu_items]
    global_operator_extra_links = [MockOperatorLink()]
    operator_extra_links = [MockOperatorLink()]
    macros = [plugin_macro]


class TestPluginBase:
    def setup_method(self) -> None:
        self.mock_plugin = MockPlugin()
        self.mock_plugin.name = "test_plugin"

        self.mock_plugin_2 = MockPlugin()
        self.mock_plugin_2.name = "test_plugin_2"


class TestPluginSchema(TestPluginBase):
    def test_serialize(self):
        deserialized_plugin = plugin_schema.dump(self.mock_plugin)
        assert deserialized_plugin == {
            "appbuilder_menu_items": [appbuilder_menu_items],
            "appbuilder_views": [{"view": self.mock_plugin.appbuilder_views[0]["view"]}],
            "flask_blueprints": [str(bp)],
            "fastapi_apps": [
                {"app": app, "name": "App name", "url_prefix": "/some_prefix"},
            ],
            "global_operator_extra_links": [str(MockOperatorLink())],
            "macros": [str(plugin_macro)],
            "operator_extra_links": [str(MockOperatorLink())],
            "source": None,
            "name": "test_plugin",
            "listeners": [],
            "timetables": [],
        }


class TestPluginCollectionSchema(TestPluginBase):
    def test_serialize(self):
        plugins = [self.mock_plugin, self.mock_plugin_2]

        deserialized = plugin_collection_schema.dump(PluginCollection(plugins=plugins, total_entries=2))
        assert deserialized == {
            "plugins": [
                {
                    "appbuilder_menu_items": [appbuilder_menu_items],
                    "appbuilder_views": [{"view": self.mock_plugin.appbuilder_views[0]["view"]}],
                    "flask_blueprints": [str(bp)],
                    "fastapi_apps": [
                        {"app": app, "name": "App name", "url_prefix": "/some_prefix"},
                    ],
                    "global_operator_extra_links": [str(MockOperatorLink())],
                    "macros": [str(plugin_macro)],
                    "operator_extra_links": [str(MockOperatorLink())],
                    "source": None,
                    "name": "test_plugin",
                    "listeners": [],
                    "timetables": [],
                },
                {
                    "appbuilder_menu_items": [appbuilder_menu_items],
                    "appbuilder_views": [{"view": self.mock_plugin.appbuilder_views[0]["view"]}],
                    "flask_blueprints": [str(bp)],
                    "fastapi_apps": [
                        {"app": app, "name": "App name", "url_prefix": "/some_prefix"},
                    ],
                    "global_operator_extra_links": [str(MockOperatorLink())],
                    "macros": [str(plugin_macro)],
                    "operator_extra_links": [str(MockOperatorLink())],
                    "source": None,
                    "name": "test_plugin_2",
                    "listeners": [],
                    "timetables": [],
                },
            ],
            "total_entries": 2,
        }
