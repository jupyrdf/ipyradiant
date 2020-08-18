import ipywidgets as ipyw
import traitlets as trt


class PredicateSelectionWidget(ipyw.HBox):
    available_predicates = trt.Instance(ipyw.SelectMultiple)
    predicates_to_collapse = trt.Instance(ipyw.SelectMultiple)
    add_button = trt.Instance(ipyw.Button)
    remove_button = trt.Instance(ipyw.Button)
    collapse_literals = trt.Instance(ipyw.Checkbox)
    show_literals = trt.Instance(ipyw.Checkbox)
    data = trt.List()
    available_preds_list = trt.List()
    remove_preds_list = trt.List(default_value=[])
    output = ipyw.Output()

    @trt.default("available_preds_list")
    def _make_available_preds_list(self):
        return self.data

    @trt.default("available_predicates")
    def _make_available_predicates(self):
        pred_selector = ipyw.SelectMultiple(
            options=self.available_preds_list,
            disabled=False,
            layout=ipyw.Layout(height="300px"),
        )
        return pred_selector

    @trt.default("predicates_to_collapse")
    def _make_preds_to_collapse(self):
        preds_to_collapse = ipyw.SelectMultiple(
            options=self.remove_preds_list,
            disabled=False,
            layout=ipyw.Layout(height="300px"),
        )
        return preds_to_collapse

    @trt.default("add_button")
    def _make_add_button(self):
        return ipyw.Button(description="Add",)

    @trt.default("remove_button")
    def _make_remove_button(self):
        return ipyw.Button(description="Remove")

    @trt.default("collapse_literals")
    def _make_collapse_lits(self):
        return ipyw.Checkbox(description="Collapse Literals?")

    @trt.default("show_literals")
    def _make_show_lits(self):
        return ipyw.Checkbox(description="Show Literals?")

    def on_add_clicked(self, *args):
        items_to_move = self.available_predicates.value
        for item in items_to_move:
            self.available_preds_list.remove(item)
            self.remove_preds_list.append(item)
        self.available_predicates.options = self.available_preds_list
        self.predicates_to_collapse.options = self.remove_preds_list

    def on_remove_clicked(self, *args):
        items_to_move = self.predicates_to_collapse.value
        for item in items_to_move:
            self.remove_preds_list.remove(item)
            self.available_preds_list.append(item)
        self.available_predicates.options = self.available_preds_list
        self.predicates_to_collapse.options = self.remove_preds_list

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = kwargs["data"]

        self.column_one = ipyw.VBox(
            children=[
                ipyw.HTML("<h1>Available Predicates</h1>"),
                self.available_predicates,
                self.collapse_literals,
            ]
        )
        self.column_two = ipyw.VBox(children=[self.add_button, self.remove_button])
        self.column_three = ipyw.VBox(
            children=[
                ipyw.HTML("<h1>Predicates to Collapse</h1>"),
                self.predicates_to_collapse,
                self.show_literals,
            ]
        )

        self.add_button.style.button_color = "lightgreen"
        self.remove_button.style.button_color = "red"
        self.add_button.layout = ipyw.Layout(margin="100px 0px 0px 0px")
        self.remove_button.layout = ipyw.Layout(margin="0px 0px 0px 0px")

        self.add_button.on_click(self.on_add_clicked)
        self.remove_button.on_click(self.on_remove_clicked)
        self.children = [self.column_one, self.column_two, self.column_three]
