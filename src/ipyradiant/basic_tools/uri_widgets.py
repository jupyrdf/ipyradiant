import ipywidgets as W
import traitlets as T


class URIContainer(W.widget.Widget):
    """A container for referencing URI Classes (e.g. with custom repr) via URI."""
    uris = T.List()
    uri_dict = T.Dict()

    def __init__(self, uris, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if uris is None:
            raise ValueError("Input 'uris' cannot be NoneType.")

        # TODO relax this requirement
        assert len(set(map(type, uris))) < 2, "All URIs must be of the same type."
        assert all(map(lambda x: hasattr(x, "uri"),
                       uris)), "URI objects must have a 'uri' attr."

        self.uris = uris

    @T.observe("uris")
    def update_uris(self, change):
        self.uris = change.new
        self.update_uri_dict()

    def update_uri_dict(self):
        self.uri_dict = dict([(uri.uri, uri) for uri in self.uris])


class SelectMultipleURI(W.SelectMultiple):
    """TODO

    object_value is the list of objects that the value (i.e. URI) came from (e.g. uri_dict.values)
    """
    uris = T.List()
    uri_dict = T.Dict()
    object_value = T.Tuple().tag(default=())

    def __init__(self, container: URIContainer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uris = container.uris
        self.uri_dict = container.uri_dict

        T.link((self, "uris"), (container, "uris"))
        T.link((self, "uri_dict"), (container, "uri_dict"))

        ordered_keys = [uri.uri for uri in self.uris]
        self.options = sorted(
            list(zip(self.uris, ordered_keys)),
            key=lambda x: str(x[0])
        )

    @T.observe("uris")
    def update_uris(self, change):
        self.value = ()
        self.object_value = ()
        ordered_keys = [uri.uri for uri in self.uris]
        self.options = sorted(
            list(zip(self.uris, ordered_keys)),
            key=lambda x: str(x[0])
        )

    @T.observe("value")
    def update_object_value(self, change):
        if not (change.new is None or len(change.new) == 0):
            self.object_value = tuple([
                self.uri_dict[uri] for (uri) in change.new
            ])
