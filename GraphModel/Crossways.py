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


    def import_crossways(self, file):
        with self.driver.session() as session:
            result = session.write_transaction(self._import_crossways, file)
            return result

    @staticmethod
    def _import_crossways(tx, file):
        result = tx.run("""
                        CALL apoc.load.csv($file) YIELD map as lines MERGE(n:Crossing:CrossWay {id : lines.id_num}) ON CREATE SET 
                        n.osm_id = lines.id, n.geometry = lines.geometry, 
                        n.crossing=lines.crossing, n.bicycle=lines.bicycle, n.closest_lanes = lines.closest_lanes, 
                        n.closest_footways = lines.closest_footways
                    """, file=file)

        return result.values()


    def import_crossways_in_spatial_layer(self):
         with self.driver.session() as session:
            result = session.write_transaction(self._import_crossways_in_spatial_layer)
            return result

    @staticmethod
    def _import_crossways_in_spatial_layer(tx):
        result = tx.run("""
                       match(n:CrossWay) with collect(n) as crossway UNWIND crossway AS cw 
                       CALL spatial.addNode('spatial', cw) yield node return node
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
                        help="""Insert the name of the .csv file.""",
                        required=True)
    return parser


def main(args=None):
    argParser = add_options()
    options = argParser.parse_args(args=args)
    greeter = App(options.neo4jURL, options.neo4juser, options.neo4jpwd)


    greeter.import_crossways(options.file_name)
    print("import crossing_ways.csv: done")

    greeter.import_crossways_in_spatial_layer()
    print("Import crossways in the spatial layer: done")



    return 0


main()