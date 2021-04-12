# Copyright (c) 2021 ipyradiant contributors.
# Distributed under the terms of the Modified BSD License.
from ipyradiant.query.framer import SPARQLQueryFramer, build_values


class TestFrame1(SPARQLQueryFramer):
    sparql = """
    SELECT DISTINCT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
    """


class TestFrame2(SPARQLQueryFramer):
    sparql = """
    SELECT DISTINCT ?p ?o
    WHERE {
        ns:Protagonist ?p ?o .
    }
    """


class TestFrame3(SPARQLQueryFramer):
    sparql = """
    SELECT DISTINCT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
    """
    columns = ["subject", "predicate", "object"]


class TestFrame4(SPARQLQueryFramer):
    sparql = """
    SELECT DISTINCT ?s ?p ?o
    WHERE {
        ?s ?p ?o .
    }
    LIMIT 1
    """


class TestMetaclass(type):
    """Metaclass to query for specific VALUES."""

    _sparql = """
        SELECT DISTINCT ?subject ?type
        WHERE {{
            ?subject a ?type .

            VALUES ({}) {{
                {}
            }}
        }}
        ORDER BY DESC(?type)
    """
    values = None

    @property
    def sparql(cls):
        return build_values(cls._sparql, cls.values)


class TestFrame5(SPARQLQueryFramer, metaclass=TestMetaclass):
    values = None


class TestFramer:
    # TODO how to move fixture to class attribute? pytest auto_use?

    def test_framer_run_query(self, simple_rdf_graph):
        res_df = TestFrame1.run_query(simple_rdf_graph)
        assert len(res_df)

    def test_framer_namespace(self, simple_rdf_graph, example_ns):
        """Test the framer to ensure that different configurations of the namespace
        (class attr, kwarg, etc.) provide proper SPARQL query execution.
        """

        # test without namespace (expect to fail)
        try:
            _ = TestFrame2.run_query(simple_rdf_graph)
            raise Exception(
                "Query execution with undefined namespace should have failed."
            )
        except Exception:
            # Expected failure
            pass

        # test with namespace at runtime
        res_df = TestFrame2.run_query(simple_rdf_graph, initNs={"ns": example_ns})
        assert len(
            res_df
        ), "Query failed to execute when running with namespace definition at runtime."

        # test with initNs classattr
        TestFrame2.initNs = {"ns": example_ns}
        res_df = TestFrame2.run_query(simple_rdf_graph)
        assert len(
            res_df
        ), "Query failed to execute when running with framer class namespace definition."

        # # test with initNs classattr/runtime w/ same namespace (expect to fail)
        # try:
        #     _ = TestFrame2.run_query(simple_rdf_graph, initNs={"ns": example_ns})
        #     raise Exception(
        #         "Multiple occurances of the same namespace should trigger exception in framer."
        #     )
        # except Exception:
        #     # Expected failure
        #     pass

    def test_framer_class_bindings(self, simple_rdf_graph, example_ns):
        """Test the framer to ensure that different configurations of the classBindings
        (class attr, kwarg, etc.) provide proper SPARQL query execution.
        """

        # test without bindings (expect all triples)
        res_df = TestFrame1.run_query(simple_rdf_graph)
        assert len(res_df) == len(
            simple_rdf_graph
        ), "Expected query without bindings to return all triples in the graph."

        # test with classBindings attr
        TestFrame1.classBindings = {"s": example_ns.Protagonist}
        res_df = TestFrame1.run_query(simple_rdf_graph)
        exp_len = len(
            list(simple_rdf_graph.triples((example_ns.Protagonist, None, None)))
        )
        assert (
            len(res_df) == exp_len
        ), "Query failed to execute when running with framer classBindings."

        # Revert class attribute
        TestFrame1.classBindings = {}

    def test_framer_init_bindings(self, simple_rdf_graph, example_ns):
        """Test the framer to ensure that different configurations of the initBindings
        provide proper SPARQL query execution.
        """

        test_query_instance = TestFrame1()

        # test without bindings already covered by test_framer_class_bindings()

        # test with initBindings explicit kwarg
        res_df = test_query_instance.run_query(
            simple_rdf_graph, initBindings={"s": example_ns.Protagonist}
        )
        exp_len = len(
            list(simple_rdf_graph.triples((example_ns.Protagonist, None, None)))
        )
        assert (
            len(res_df) == exp_len
        ), "Query failed to execute when running with explicit initBindings kwarg."

        # test with initBindings passed as kwarg
        res_df = test_query_instance.run_query(
            simple_rdf_graph, s=example_ns.Protagonist
        )
        exp_len = len(
            list(simple_rdf_graph.triples((example_ns.Protagonist, None, None)))
        )
        assert (
            len(res_df) == exp_len
        ), "Query failed to execute when running with initBindings as kwargs."

    def test_framer_columns(self, simple_rdf_graph):
        """Test to make sure columns are set successfully."""

        # Test default columns
        res_df = TestFrame1.run_query(simple_rdf_graph)
        assert " ".join(list(res_df.columns)) == "s p o"

        # Test custom columns
        res_df = TestFrame3.run_query(simple_rdf_graph)
        assert " ".join(list(res_df.columns)) == " ".join(TestFrame3.columns)

    def test_framer_index(self, simple_rdf_graph):
        """Test setting an index for the DataFrame results on the framer."""

        # test simple index
        TestFrame1.index = ["s"]
        res_df = TestFrame1.run_query(simple_rdf_graph)
        assert len(list(res_df.columns)) == 2, "Failed to set index on framer."

        # Revert class attribute
        TestFrame1.index = []
        res_df = TestFrame1.run_query(simple_rdf_graph)
        assert len(list(res_df.columns)) == 3, "Failed to revert index on framer."

    def test_framer_query_parsing(self, simple_rdf_graph):
        """Verify that query parsing for repeat query execution is working.

        TODO test that the query is re-parsed when the namespace or sparql string is changed
        """
        assert (
            TestFrame4.query is None and TestFrame4.p_sparql == ""
        ), "Test query class was executed prior to testing."

        res_df = TestFrame4.run_query(simple_rdf_graph)
        assert len(res_df) == 1, "Failed to return the expected query results."
        assert (
            TestFrame4.query is not None
        ), "Failed to store the parsed query on the framer class."
        assert (
            TestFrame4.p_sparql != ""
        ), "Failed to store the previous sparql state on the framer class"

        # Run to make sure the execution doesn't throw errors when using the parsed query attribute
        res_df = TestFrame4.run_query(simple_rdf_graph)
        assert len(res_df) == 1, "Failed to return the expected query results."


class TestFramerMetaclass:
    # TODO how to move fixture to class attribute? pytest auto_use?

    def test_framer_metaclass_without_values(self, simple_rdf_graph):
        try:
            _ = TestFrame5.run_query(simple_rdf_graph)
            raise Exception("Expected a query with undefined VALUES to fail.")
        except AssertionError:
            # Expected this to fail
            pass

    def test_framer_metaclass_with_values(self, simple_rdf_graph, SCHEMA):
        TestFrame5.values = {"type": [SCHEMA.Person]}
        res_df = TestFrame5.run_query(simple_rdf_graph)
        assert (
            len(set(res_df.type)) == 1
        ), "Failed to return query results when applying VALUES to metaclass."

        # Revert class attribute
        TestFrame5.values = None
