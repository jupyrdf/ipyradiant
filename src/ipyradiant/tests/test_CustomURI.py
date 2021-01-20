# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
import unittest

from rdflib import Graph, URIRef

from ipyradiant import CustomURIRef


class Testing(unittest.TestCase):
    namespaces = {"ex": "www.example.org/"}
    graph = Graph()

    def __init__(self, *args, **kwargs):
        super(Testing, self).__init__(*args, **kwargs)
        for key, value in self.namespaces.items():
            self.graph.namespace_manager.bind(key, value)

    # start by testing functionality of CustomURIRef class
    def test1(self):
        custom = CustomURIRef(
            uri=URIRef("www.example.org/1"), namespaces=self.namespaces
        )
        normal = URIRef("www.example.org/1")
        self.assertEqual(custom, normal)

    def test2(self):
        custom = str(
            CustomURIRef(uri=URIRef("www.example.org/1"), namespaces=self.namespaces)
        )
        normal = "ex:1"
        self.assertEqual(custom, normal)

    def test3(self):
        # now do similar stuff but with a NamespaceManager object instead...
        custom = CustomURIRef(
            uri=URIRef("www.example.org/1"), namespaces=self.graph.namespace_manager
        )
        normal = URIRef("www.example.org/1")
        self.assertEqual(custom, normal)

    def test4(self):
        custom = str(
            CustomURIRef(
                uri=URIRef("www.example.org/1"), namespaces=self.graph.namespace_manager
            )
        )
        normal = "ex:1"
        self.assertEqual(custom, normal)

    def test5(self):
        custom = CustomURIRef(
            uri=URIRef("www.example.org/1"), namespaces=self.namespaces
        )
        normal = URIRef("www.example.org/2")
        self.assertNotEqual(custom, normal)
