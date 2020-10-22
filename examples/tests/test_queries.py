import unittest

import rdflib
from SPARQLWrapper import JSON, SPARQLWrapper


class QueryTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(QueryTests, self).__init__(*args, **kwargs)

    # Remote Query Test
    def test1(self):
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery(
            """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?label
            WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
            """
        )

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        res = []
        for result in results["results"]["bindings"]:
            res.append(result["label"]["value"])

        self.assertEqual(
            res,
            [
                "Asturias",
                "منطقة أستورياس",
                "Asturien",
                "Asturias",
                "Asturies",
                "Asturie",
                "アストゥリアス州",
                "Asturië (regio)",
                "Asturia",
                "Astúrias",
                "Астурия",
                "阿斯图里亚斯",
            ],
        )

    # Federated Query Test
    def test2(self):
        graph = rdflib.Graph()
        query_str = """
            SELECT DISTINCT ?s ?p ?o
            WHERE
            { service <http://linkeddata.uriburner.com/sparql> {SELECT ?s ?p ?oWHERE {?s ?p ?o}LIMIT 3                }}
        """
        res = graph.query(query_str)
        res = list(res)
        self.assertEqual(
            res,
            [
                (
                    rdflib.term.URIRef("https://i.imgur.com/0HuwV7e.jpg"),
                    rdflib.term.URIRef(
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                    ),
                    rdflib.term.URIRef("http://www.w3.org/2001/XMLSchema#anyURI"),
                ),
                (
                    rdflib.term.URIRef("https://i.imgur.com/4OESFVu.jpg"),
                    rdflib.term.URIRef(
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                    ),
                    rdflib.term.URIRef("http://www.w3.org/2001/XMLSchema#anyURI"),
                ),
                (
                    rdflib.term.URIRef("https://i.imgur.com/53l1jxR.jpg"),
                    rdflib.term.URIRef(
                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                    ),
                    rdflib.term.URIRef("http://www.w3.org/2001/XMLSchema#anyURI"),
                ),
            ],
        )
