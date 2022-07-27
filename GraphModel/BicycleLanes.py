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


    def import_bicycle_lanes(self, file):
        with self.driver.session() as session:
            result = session.write_transaction(self._import_bicycle_lanes, file)
            return result

    @staticmethod
    def _import_bicycle_lanes(tx, file):
        result = tx.run("""
                        CALL apoc.load.csv($file) YIELD map as lines 
                        MERGE(n:BicycleLane {id_num : lines.id_num}) ON CREATE SET n.osm_id = lines.id, n.ID_E = lines.ID_E, 
                        n. geometry = lines.geometry, 
                        n.highway=lines.highway, n.bicycle=lines.bicycle, n.foot=lines.foot, 
                        n.lanes=lines.lanes, n.cycleway=lines.cycleway, n.segregated=lines.segregated,
                        n.classifica=lines.classifica, n.touched_lanes = lines.touched_lanes
                    """, file=file)

        return result.values()


    def import_lanes_in_spatial_layer(self):
         with self.driver.session() as session:
            result = session.write_transaction(self._import_lanes_in_spatial_layer)
            return result

    @staticmethod
    def _import_lanes_in_spatial_layer(tx):
        result = tx.run("""
                       match(n:BicycleLane) with collect(n) as lanes UNWIND lanes AS l CALL spatial.addNode('spatial', l) yield node return node
        """)
                        
        return result.values()


    def add_index(self):
         with self.driver.session() as session:
            result = session.write_transaction(self._add_index)
            return result

    @staticmethod
    def _add_index(tx):
        result = tx.run("""
                       create index cicleway_index for (n:BicycleLane) on (n.id_num)
        """)
                        
        return result.values()    



    def find_intersected_lanes(self):
        with self.driver.session() as session:
            result = session.write_transaction(self._find_intersected_lanes)
            return result

    @staticmethod
    def _find_intersected_lanes(tx):
        result = tx.run("""
                    match(n:BicycleLane) with collect(n) as lanes UNWIND lanes as l 
                    call spatial.intersects('spatial', l.geometry) yield node UNWIND node as p 
                    match(n:BicycleLane) where n.id_num=l.id_num AND p.id_num <> n.id_num AND p:BicycleLane merge(n)-[:CONTINUE_ON_LANE]->(p) return p, n
        
        """)

        return result.values()


    def find_touched_lanes(self):
         with self.driver.session() as session:
            result = session.write_transaction(self._find_touched_lanes)
            return result

    
    @staticmethod
    def _find_touched_lanes(tx):
        result = tx.run("""
                match(n:BicycleLane) where n.touched_lanes <> "[]" set n.touched_lanes=replace(n.touched_lanes, "["," "); 
        """)

        result = tx.run("""
                match(n:BicycleLane) where n.touched_lanes <> "[]" set n.touched_lanes=replace(n.touched_lanes, "]"," "); 
        """)

        result = tx.run(""" 
                match(n:BicycleLane) where n.touched_lanes <> "[]" set n.touched_lanes=replace(n.touched_lanes, "'","");
        """)

        result = tx.run("""
                match(n:BicycleLane) where n.touched_lanes <> "[]" unwind split(n.touched_lanes, ",") as lane match(n1:BicycleLane) where n1.id_num=trim(lane) 
                and n1.touched_lanes <> "[]" and n.geometry <> n1.geometry merge (n)-[:CONTINUE_ON_LANE]->(n1)
        """)

        #result = tx.run("""
        #    match(n:BicycleLane) remove n.touched_lanes; 
        #""")

        return result

    
    def find_nearest_lanes(self):
         with self.driver.session() as session:
            result = session.write_transaction(self._find_nearest_lanes)
            return result


    
    @staticmethod
    def _find_nearest_lanes(tx):
        result = tx.run("""
            match(n:BicycleLane) where n.nearest_lanes <> "[]" set n.nearest_lanes=replace(n.nearest_lanes, "["," "); 
        """)


        result = tx.run("""
            match(n:BicycleLane) where n.nearest_lanes <> "[]" set n.nearest_lanes=replace(n.nearest_lanes, "]"," "); 
        """)


        result = tx.run("""
            match(n:BicycleLane) where n.nearest_lanes <> "[]" set  n.nearest_lanes=replace(n.nearest_lanes, "'","");
        """)


        result = tx.run("""
            match(n:BicycleLane) where n.nearest_lanes <> "[]" unwind split(n.nearest_lanes, ",") as lane match(n1:BicycleLane) 
            where n1.id_num=trim(lane) and n1.nearest_lanes <> "[]" and n.geometry <> n1.geometry merge (n)-[:CONTINUE_ON_LANE_BY_CROSSING_ROAD]->(n1);
        """)

        result = tx.run("""
            match(n:BicycleLane) remove n.nearest_lanes;
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
    parser.add_argument('--nameFile', '-f', dest='file_name', type=str,
                        help="""Insert the name of the .csv file.""",
                        required=True)
    return parser


def main(args=None):
    argParser = add_options()
    options = argParser.parse_args(args=args)
    greeter = App(options.neo4jURL, options.neo4juser, options.neo4jpwd)

    start_time = time.time()
    #greeter.import_bicycle_lanes(options.file_name)
    #print("import ciclabili.csv: done")

    #greeter.import_lanes_in_spatial_layer()
    #print("Import the lanes in the spatial layer: done")

    greeter.add_index()
    print("Add an index on the id_num : done")

    greeter.find_intersected_lanes()
    print("Find the intersected lanes: done")

    greeter.find_touched_lanes()
    print("Find the lanes that touches each other: done")
    #print("Execution time : %s seconds" % (time.time() - start_time))

    #greeter.find_nearest_lanes()
    #print('Find the lanes that are close to each other: done')


    return 0


main()