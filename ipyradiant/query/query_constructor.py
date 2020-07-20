""" a query constructor
"""
# pylint: disable=C0103,C0115,C0116,C0116,R0201,R0901,W0511,W0613
import ipywidgets as W
import traitlets as T

from .query_form import QueryInput

# TODO improve
query_template = """{}
{}
WHERE {{
    {}
}}
{}
{}
"""


class QueryConstructor(W.HBox):
    """TODO
    - way better templating and more efficient formatting
    - replace individual observers with larger observer
    - move build_query to standalone function
    """

    convert_arrow = T.Instance(W.Image)
    query_input = T.Instance(W.VBox)
    formatted_query = T.Instance(W.Textarea)

    # traits from children
    namespaces = T.Unicode()
    query_type = T.Unicode()
    query_line = T.Any()
    query_body = T.Unicode()
    limit_value = T.Int()
    limit_enabled = T.Bool()
    offset_value = T.Int()

    log = W.Output()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_input = QueryInput()

        # Inherit traits with links TODO easier way?
        T.link((self.query_input.namespaces, "namespaces"), (self, "namespaces"))
        T.link((self.query_input.header, "dropdown_value"), (self, "query_type"))
        T.link((self.query_input.header, "header_value"), (self, "query_line"))
        T.link((self.query_input.body.body, "value"), (self, "query_body"))
        T.link((self.query_input.lim_and_off.limit, "value"), (self, "limit_value"))
        T.link((self.query_input.lim_and_off, "limit_enabled"), (self, "limit_enabled"))
        T.link((self.query_input.lim_and_off.offset, "value"), (self, "offset_value"))

        self.children = tuple([self.query_input, self.formatted_query])

    def build_query(self):
        # get values TODO improve
        namespaces = self.namespaces
        query_type = self.query_type
        query_line = self.query_line
        query_body = self.query_body or self.query_input.body.body.placeholder
        limit = self.limit_value if self.limit_enabled else None
        offset = self.offset_value

        # update query_body
        query_body = "\t\n".join(
            query_body.split("\n")
        )  # TODO this isn't actually formatting properly

        # placeholder strings
        header_str = ""
        limit_str = ""
        offset_str = ""

        # TODO move these to module vars
        if query_type in {"SELECT", "SELECT DISTINCT"}:
            if query_line == "":
                query_line = "*"
            header_str = f"{query_type} {query_line}"
            if limit is not None:
                limit_str = f"LIMIT {limit}"
            if offset > 0:
                offset_str = f"OFFSET {offset}"
        elif query_type == "ASK":
            header_str = query_type
        elif query_type == "CONSTRUCT":
            header_str = "CONSTRUCT {\n" + query_line + "\n}"
        else:
            with self.log:
                raise ValueError(f"Unexpected query type: {query_type}")

        return query_template.format(
            namespaces, header_str, query_body, limit_str, offset_str
        )

    @T.default("formatted_query")
    def make_default_formatted_query(self):
        formatted_query = W.Textarea(
            placeholder="Formatted query will appear here...",
            layout=W.Layout(height="260px", width="50%"),
        )
        return formatted_query

    @T.observe(
        "namespaces",
        "query_type",
        "query_line",
        "query_body",
        "limit_value",
        "limit_enabled",
        "offset_value",
    )
    def update_query(self, change):
        self.formatted_query.value = self.build_query()
