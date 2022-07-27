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

    def connect_lanes_to_crossing_nodes(self):
        with self.driver.session() as session:
            result = session.write_transaction(self._connect_lanes_to_crossing_nodes)
            return result


    @staticmethod
    def _connect_lanes_to_crossing_nodes(tx):
        result = tx.run("""
            match(n:CrossNode) with n call spatial.withinDistance("spatial", n.location, 0.009) yield node 
            unwind(node) as ob match(n1) where n1.id_num=ob.id_num and not ob:Neighborhood and n.geometry <> ob.geometry and ob:BicycleLane 
            merge (ob)-[:CROSS_THE_ROAD]->(n);
        """)

        result = tx.run("""
            match(n:CrossNode)<-[:CROSS_THE_ROAD]-(p:BicycleLane) with n, p 
            merge (n)-[:CROSS_THE_ROAD]->(p); 

        """)
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
    greeter.connect_lanes_to_crossing_nodes()
    print("Connect elements close to the crossing nodes: done")
    print("Execution time : %s seconds" % (time.time() - start_time))


    

    return 0


main()