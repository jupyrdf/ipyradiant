# Copyright (c) 2020 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.


import traitlets as trt

import ipywidgets as ipyw


class MultiPanelSelect(ipyw.HBox):
    available_things = trt.Instance(ipyw.SelectMultiple)
    selected_things = trt.Instance(ipyw.SelectMultiple)
    add_button = trt.Instance(ipyw.Button)
    remove_button = trt.Instance(ipyw.Button)
    data = trt.List()
    available_things_list = trt.List()
    selected_things_list = trt.List(default_value=[])
    output = ipyw.Output()

    @trt.default("available_things_list")
    def _make_available_things_list(self):
        return self.data

    @trt.default("available_things")
    def _make_available_things(self):
        thing_selector = ipyw.SelectMultiple(
            options=self.available_things_list,
            disabled=False,
            layout=ipyw.Layout(height="300px"),
        )
        return thing_selector

    @trt.default("selected_things")
    def _make_selected_things(self):
        selected_things = ipyw.SelectMultiple(
            options=self.selected_things_list,
            disabled=False,
            layout=ipyw.Layout(height="300px"),
        )
        return selected_things

    @trt.default("add_button")
    def _make_add_button(self):
        return ipyw.Button(description="Add",)

    @trt.default("remove_button")
    def _make_remove_button(self):
        return ipyw.Button(description="Remove")

    def on_add_clicked(self, *args):
        items_to_move = self.available_things.value
        for item in items_to_move:
            self.available_things_list.remove(item)
            self.selected_things_list.append(item)
        self.available_things.options = self.available_things_list
        self.selected_things.options = self.selected_things_list

    def on_remove_clicked(self, *args):
        items_to_move = self.selected_things.value
        for item in items_to_move:
            self.selected_things_list.remove(item)
            self.available_things_list.append(item)
        self.available_things.options = self.available_things_list
        self.selected_things.options = self.selected_things_list

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = kwargs["data"]

        self.column_one = ipyw.VBox(
            children=[ipyw.HTML("<h1>Available Things</h1>"), self.available_things]
        )
        self.column_two = ipyw.VBox(children=[self.add_button, self.remove_button])
        self.column_three = ipyw.VBox(
            children=[ipyw.HTML("<h1>Selected Things</h1>"), self.selected_things]
        )

        self.add_button.style.button_color = "lightgreen"
        self.remove_button.style.button_color = "red"
        self.add_button.layout = ipyw.Layout(margin="100px 0px 0px 0px")
        self.remove_button.layout = ipyw.Layout(margin="0px 0px 0px 0px")

        self.add_button.on_click(self.on_add_clicked)
        self.remove_button.on_click(self.on_remove_clicked)
        self.children = [self.column_one, self.column_two, self.column_three]
