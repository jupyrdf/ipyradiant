# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import ipywidgets as ipyw
import traitlets as trt


class MultiPanelSelect(ipyw.HBox):
    available_things = trt.Instance(ipyw.SelectMultiple)
    selected_things = trt.Instance(ipyw.SelectMultiple)
    add_button = trt.Instance(ipyw.Button)
    remove_button = trt.Instance(ipyw.Button)
    data = trt.List()
    available_things_list = trt.List(default_value=[])
    selected_things_list = trt.List(default_value=[])
    output = ipyw.Output()
    column_one = trt.Instance(ipyw.VBox)
    column_two = trt.Instance(ipyw.VBox)
    column_three = trt.Instance(ipyw.VBox)
    left_panel_text = trt.Unicode(default_value="Available Things")
    right_panel_text = trt.Unicode(default_value="Selected Things")

    @trt.default("column_one")
    def _make_column_one(self):
        return ipyw.VBox(
            children=[
                ipyw.HTML(f"<b>{self.left_panel_text}</b>"),
                self.available_things,
            ]
        )

    @trt.default("column_two")
    def _make_column_two(self):
        return ipyw.VBox(children=[self.add_button, self.remove_button])

    @trt.default("column_three")
    def _make_column_three(self):
        return ipyw.VBox(
            children=[
                ipyw.HTML(f"<b>{self.right_panel_text}</b>"),
                self.selected_things,
            ]
        )

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
        return ipyw.Button(
            description="Add -->".center(12),
        )

    @trt.default("remove_button")
    def _make_remove_button(self):
        return ipyw.Button(description="<-- Remove".center(12))

    @trt.observe("data")
    def _change_data(self, change):
        self.available_things_list = self._make_available_things_list()

    @trt.observe("available_things_list")
    def _change_selector(self, change):
        self.available_things = self._make_available_things()

    @trt.observe("selected_things_list")
    def _change_selected_items(self, change):
        self.selected_things = self._make_selected_things()

    @trt.observe(
        "selected_things", "available_things", "right_panel_text", "left_panel_text"
    )
    def _update_columns(self, change):
        """
        In this function we are referring to the three 'columns' of the HBox as column_one,
        column_two, and column_three. We are using this function to update the display and contents
        of each of these columns. For example, column_one consists of the HTML title and then the available_things widget,
        column_two consists of the add/remove buttons, and column_three consists of the other HTML title and the selected_things widget.
        """
        self.column_one = self._make_column_one()
        self.column_two = self._make_column_two()
        self.column_three = self._make_column_three()
        self._update_ui()

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
        """A multi-select widget that uses multiple panels to improve widget state
        clarity.

        Available kwargs:
          :data: the list of things that will appear in the panels
          :left_panel_text: the text to use when creating the left panel label
          :right_panel_text: the text to use when creating the right panel label

        TODO allow other types of data (e.g. dict)
        TODO allow for more flexible styling
        """
        super().__init__(*args, **kwargs)
        self.data = kwargs["data"]
        self.left_panel_text = kwargs.get("left_panel_text", "Available Things")
        self.right_panel_text = kwargs.get("right_panel_text", "Selected Things")

        # TODO improve layout, design and stability
        self.add_button.layout = ipyw.Layout(margin="100px 0px 0px 0px")
        self.remove_button.layout = ipyw.Layout(margin="0px 0px 0px 0px")

        self.add_button.on_click(self.on_add_clicked)
        self.remove_button.on_click(self.on_remove_clicked)
        self._update_ui()

    def _update_ui(self):
        self.children = [self.column_one, self.column_two, self.column_three]
