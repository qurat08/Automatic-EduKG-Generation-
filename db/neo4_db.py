from neo4j import GraphDatabase
import numpy as np
import logging
from log import LOG

logger = LOG(name=__name__, level=logging.DEBUG)


class NeoDataBase:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri,
                                           auth=(user, password),
                                           encrypted=False)

    def close(self):
        self.driver.close()

    def get_or_create_concepts_and_relationships(self, materialId,
                                                 materialName, data):
        """
        """
        session = self.driver.session()
        tx = session.begin_transaction()
        concepts = []
        relations = []
        try:
            _mid = self.get_learning_material(tx, materialId)
            if _mid:
                logger.info("Found learning material '%s" % materialId)
                concepts = self.retrieve_all_concepts(tx, materialId)
                relations = self.retrieve_relationships(tx, materialId)
            else:
                logger.info("Could not find learning material '%s" %
                            materialId)
                self.create_learning_material(tx, materialId, materialName)
                # concepts

                logger.info("Creating concepts for learning material '%s'" %
                            materialId)
                for node in data:
                    self.create_concept(tx, node)

                # relationships
                logger.info(
                    "Creating relationships for learning material '%s'" %
                    materialId)
                for node in data:
                    self.create_concept_relationships(tx, node)

                self.create_lr_relationships(tx, materialId)
                concepts = self.retrieve_all_concepts(tx, materialId)
                relations = self.retrieve_relationships(tx, materialId)
            tx.commit()
        except Exception as e:
            logger.error("Failure retrieving or creating concepts - %s" % e)
            tx.rollback()
            session.close()
            self.close()
            concepts = []
            relations = []

        return concepts, relations

    def create_concept(self, tx, node):
        """
        """
        tx.run(
            """MERGE (c:Concept {name: $name, cid: $cid, uri: $uri, type: $type, mid: $mid, weight: $weight, wikipedia: $wikipedia, abstract: $abstract,initial_embedding:$initial_embedding,
            final_embedding:$final_embedding})""",
            name=node["name"],
            cid=node["id"],
            uri=node["uri"],
            type=node["type"],
            mid=node["mid"],
            weight=node["weight"],
            wikipedia=node["wikipedia"],
            initial_embedding=node["initial_embedding"],
            final_embedding="",
            abstract=node["abstract"])

    def create_concept_relationships(self, tx, node):
        """
        """
        relations = node["to"]
        for relation in relations:
            tx.run("""MATCH (a:Concept) WHERE a.cid = $s_cid AND a.mid = $mid
                OPTIONAL MATCH(b:Concept) WHERE b.cid = $t_cid AND b.mid = $mid
                MERGE (a)-[r: %s {weight: $weight}]->(b)
                """ % relation["rel_type"],
                   s_cid=node["id"],
                   t_cid=relation["id"],
                   mid=node["mid"],
                   weight=relation["weight"])

    def create_lr_relationships(self, tx, mid):
        """
        """
        logger.info(
            "Creating learning material relationships to concepts '%s'" % mid)
        tx.run("""MATCH (m:LearningMaterial) WHERE m.mid = $mid 
                OPTIONAL MATCH (c:Concept) WHERE c.mid = $mid
                MERGE (m)-[r:CONTAINS]->(c)""",
               mid=mid)

    def lm_exists(self, mid):
        """
        """
        with self.driver.session() as session:
            result = session.run(
                "MATCH (m:LearningMaterial) WHERE m.mid = $mid RETURN m",
                mid=mid)
            
            if list(result):
                return True
            else:
                return False

    def get_learning_material(self, tx, mid):
        """
        """
        result = tx.run(
            "MATCH (m:LearningMaterial) WHERE m.mid = $mid RETURN m",
            mid=mid).data()

        return list(result)

    def create_learning_material(self, tx, mid, name):
        """
        """
        logger.info("Creating learning material '%s'" % mid)
        result = tx.run(
            "MERGE (m:LearningMaterial {mid: $mid, name: $name}) RETURN m",
            mid=mid,
            name=name)
        record = result.single()
        return record["m"]

    def retrieve_all_concepts(self, tx, mid):
        """
        """
        logger.info("Geting the concepts of learning material '%s'" % mid)
        result = tx.run("""MATCH (c:Concept)
            WHERE c.mid = $mid 
            RETURN LABELS(c) as labels, ID(c) AS id, c.cid as cid, c.name AS name, c.uri as uri, c.type as type, c.weight as weight, c.wikipedia as wikipedia, c.abstract as abstract""",
                        mid=mid)

        return list(result)

    def retrieve_relationships(self, tx, mid):
        """
        """
        logger.info("Geting the relationships of learning material '%s'" % mid)
        result = tx.run("""
            MATCH p=(a)-[r]->(b) 
            WHERE TYPE(r) <> 'CONTAINS'
            AND a.mid = $mid 
            AND b.mid = $mid 
            RETURN TYPE(r) as type, ID(a) as source, ID(b) as target, r.weight as weight""",
                        mid=mid)
        
        return list(result)

    def construct_user_model(self, user,concepts):
        """
        """
        session = self.driver.session()
        tx = session.begin_transaction()

        try:
            if self.user_exists(user):
                logger.info("Found  user %s" % user["id"])
            else:
                logger.info("create  user %s" % user["id"])
                self.create_user(tx, user)
            self.connect_user_concept(tx, user,concepts)
            self.get_user_embedding(tx, user)
            tx.commit()
        except Exception as e:
            logger.error("Failure  connect user and concept" % e)
            tx.rollback()
            session.close()
            self.close()
            

    def user_exists(self, user):
        """
        """
        with self.driver.session() as session:
            result = session.run(
                "MATCH (u:User) WHERE u.uid = $uid RETURN u",
                uid=user["id"])
            if list(result):
                return True
            else:
                return False

    def create_user(self, tx, user):
        """
        """
        tx.run(
            """MERGE (u:User {name: $name, uid: $uid, type: $type, embedding:$embedding})""",
            name=user["name"],
            uid=user["id"],
            type="user",
            embedding="")

    def connect_user_concept(self, tx, user,concepts):
        """
        """
        logger.info("Connect user and concept")
        for concept in concepts:
            if concept[1] == 1:
                #If user doesn't understand the concept, the relationship is "dnu"
                tx.run("""MATCH (u:User) WHERE u.uid = $uid 
                    OPTIONAL MATCH (c:Concept) WHERE c.name = $name  And c.type <> $type
                    MERGE (u)-[r:dnu {weight: 1}]->(c)""",
                    uid=user["id"],
                    name=concept[0],
                    type="category")

                tx.run('''MATCH p=(u)-[r:u]->(c) where u.uid=$uid And c.name = $name  delete r''',
                    uid=user["id"],
                    name=concept[0])
            else:
                #If user understand the concept, the relationship is "u"
                tx.run("""MATCH (u:User) WHERE u.uid = $uid 
                    OPTIONAL MATCH (c:Concept) WHERE c.name = $name  And c.type <> $type
                    MERGE (u)-[r:u {weight: 1}]->(c)""",
                    uid=user["id"],
                    name=concept[0],
                    type="category")
                    
                tx.run('''MATCH p=(u)-[r:dnu]->(c) where u.uid=$uid And c.name = $name  delete r''',
                    uid=user["id"],
                    name=concept[0])

    def get_user_embedding(self, tx, user):
        """
        """
        #Find concept embeddings that user doesn't understand
        results = tx.run("""MATCH p=(u)-[r:dnu]->(c) where u.uid=$uid RETURN c.initial_embedding as embedding""", 
                uid=user["id"])
        embeddings = list(results)
        #If the user does not have concepts that he does not understand, the list is empty
        if not embeddings:
            tx.run("""MATCH (u:User) WHERE u.uid=$uid set u.embedding=$embedding""",
                uid=user["id"],
                embedding = "")
            logger.info("reset user embedding")
        else:
            sum = 0
            #Convert string type to array type 'np.array'
            #Sum and average these concept embeddings to get user embedding
            for embedding in embeddings:
                list1 = embedding["embedding"].split(',')
                list2 = []
                for j in list1:
                    list2.append(float(j))
                arr = np.array(list2)
                sum = sum + arr 
            average = np.divide(sum,len(embeddings))
            tx.run("""MATCH (u:User) WHERE u.uid=$uid set u.embedding=$embedding""",
                    uid=user["id"],
                    embedding = ','.join(str(i) for i in average)) 
            logger.info("get user embedding")