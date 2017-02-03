from setuptools import setup

setup(name = 'sematch',
      packages=['sematch','sematch.semantic'],
      version = '1.0.0',
      description = 'Semantic similarity framework for knowledge graphs',
      author = 'Ganggao Zhu',
      author_email = 'gzhu@dit.upm.es',
      url = 'https://github.com/gsi-upm/sematch',
      keywords = ['semantic similarity', 'taxonomy', 'knowledge graph', 
      'semantic analysis', 'knowledge base', 'WordNet', 'DBpedia','YAGO', 'ontology'], 
      classifiers = [],
      install_requires=['numpy==1.8.0','scipy==0.13.2','scikit-learn==0.17.1','networkx==1.11',
                        'nltk==3.2','rdflib==4.0.1','SPARQLWrapper==1.5.2'],
      )