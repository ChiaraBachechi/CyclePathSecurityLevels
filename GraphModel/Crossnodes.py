from neo4j import GraphDatabase
import overpy
import json
import argparse
import os


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()


    def import_crossnodes(self, file):
        with self.driver.session() as session:
            result = session.write_transaction(self._import_crossnodes, file)
            return result

    @staticmethod
    def _import_crossnodes(tx, file):
        result = tx.run("""
                        CALL apoc.load.json($file) YIELD value AS value 
                        WITH value.features AS features
                        UNWIND features AS cross
                        MERGE (n:Crossing:CrossNode {id : cross.properties.id_num})
                        ON CREATE SET n.osm_id = cross.properties.id, n.location=point({latitude:cross.geometry.coordinates[1], longitude:cross.geometry.coordinates[0]}), 
                        n.geometry='POINT(' + cross.geometry.coordinates[0] + ' ' + cross.geometry.coordinates[1] + ')', 
                        n.crossing=cross.properties.crossing, n.kerb=cross.properties.kerb, n.bicycle=cross.properties.bicycle, 
                        n.bus=cross.properties.bus, n.button_operated=cross.properties.button_operated
                    """, file=file)

        return result.values()


    def import_crossnodes_in_spatial_layer(self):
         with self.driver.session() as session:
            result = session.write_transaction(self._import_crossnodes_in_spatial_layer)
            return result

    @staticmethod
    def _import_crossnodes_in_spatial_layer(tx):
        result = tx.run("""
                       match(n:CrossNode) with collect(n) as crossnodes UNWIND crossnodes AS cn 
                       CALL spatial.addNode('spatial', cn) yield node return node
        """)
                       
        return result.values()



    



def add_options():
    parser = argparse.ArgumentParser(description='Insertion of POI in the graph.')
    parser.add_argument('--neo4jURL', '-n', dest='neo4jURL', type=str,
                        help="""Insert the address of the local neo4j instance. For example: neo4j://localhost:7687""",
                        required=True)
    parser.add_argument('--neo4juser', '-u', dest='neo4juser', type=str,
                        help="""Insert the name of the user of the local neo4j instance.""",
                        required=True)
    parser.add_argument('--neo4jpwd', '-p', dest='neo4jpwd', type=str,
                        help="""Insert the password of the local neo4j instance.""",
                        required=True)
    parser.add_argument('--nameFile', '-f', dest='file_name', type=str,
                        help="""Insert the name of the .geojson file.""",
                        required=True)
    return parser


def main(args=None):
    argParser = add_options()
    options = argParser.parse_args(args=args)
    greeter = App(options.neo4jURL, options.neo4juser, options.neo4jpwd)


    greeter.import_crossnodes(options.file_name)
    print("import crossing_nodes.json: done")

    greeter.import_crossnodes_in_spatial_layer()
    print("Import crossnodes in the spatial layer: done")



    return 0


main()