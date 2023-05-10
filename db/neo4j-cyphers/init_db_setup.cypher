CREATE CONSTRAINT constraint_unique_material IF NOT EXISTS ON ( material:LearningMaterial) ASSERT (material.mid, material.name) IS UNIQUE;
CREATE CONSTRAINT constraint_unique_concept IF NOT EXISTS ON (concept:Concept) ASSERT (concept.cid, concept.mid, concept.name, concept.type) IS UNIQUE;
