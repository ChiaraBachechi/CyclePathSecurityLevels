from neo4j import GraphDatabase
import overpy
import json
import argparse
import os
import time

class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def connect_crossways_to_bicycle_lanes(self):
        with self.driver.session() as session:
            result = session.write_transaction(self._connect_crossways_to_bicycle_lanes)
            return result


    @staticmethod
    def _connect_crossways_to_bicycle_lanes(tx):
        result = tx.run("""
            match(n:CrossWay) where n.closest_lanes <> "[]" set n.closest_lanes=replace(n.closest_lanes, "["," ");  
        """)

        result = tx.run("""
            match(n:CrossWay) where n.closest_lanes <> "[]" set n.closest_lanes=replace(n.closest_lanes, "]"," ");  
        """)

        result = tx.run("""
            match(n:CrossWay) where n.closest_lanes <> "[]" set  n.closest_lanes=replace(n.closest_lanes, "'","");   
        """)

        result = tx.run("""
            match(n:CrossWay) where n.closest_lanes <> "[]" unwind split(n.closest_lanes, ",") as lane 
            match(n1:BicycleLane) where n1.id_num=trim(lane) merge (n1)-[:CROSS_THE_ROAD]->(n);
        """)

        result = tx.run("""
            match(n:CrossWay)<-[:CROSS_THE_ROAD]-(p:BicycleLane) with n, p merge (n)-[:CROSS_THE_ROAD]->(p);  
        """)

        #result = tx.run("""
        #    match(n:CrossWay) remove n.closest_lanes;   
        #""")

        return result




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
    return parser


def main(args=None):
    argParser = add_options()
    options = argParser.parse_args(args=args)
    greeter = App(options.neo4jURL, options.neo4juser, options.neo4jpwd)

    start_time = time.time()
    greeter.connect_crossways_to_bicycle_lanes()
    print("Connect lanes to the crossing ways: done")
    print("Execution time : %s seconds" % (time.time() - start_time))


    

    return 0


main()