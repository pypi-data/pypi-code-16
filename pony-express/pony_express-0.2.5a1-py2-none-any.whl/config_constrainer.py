
import networkx as nx
import dependencies as dep

class ConfigurationImpossible(Exception):
    """Exception raised in case pony can't find an acceptable dependency configuration."""

    def __str__ (self):
        return """Can't fulfill all dependencies in a compatible way.
"""

class config_generator:
    def __init__(self, gr):
        self.gr = gr
        self.clusters = dict()

        for n in self.gr.nodes():
            try:
                self.clusters[n.NAME] += [n]
            except KeyError:
                self.clusters[n.NAME] = [n]

            self.gr.node[n]['ndep'] = self._ndep(self.gr.neighbors(n))
        
    
    def _ndep(self,requirements):
        """
        Given a requirement list, calculate the number of projects involved as dependecy.
        """

        dependant_projects = set()
        for r in requirements:
            try:
                dependant_projects.add( r.NAME )
            except KeyError:
                # ignore empty graph node for now
                pass

        return len(dependant_projects)
    def _reduce_graph(gr, removed_alternatives):
        reduced_gr = gr.copy()
        reduced_gr.remove_nodes_from( removed_alternatives)
        return resuced_gr

    def _local_constraint(self, n, configuration):
        assert type(configuration) == dict
        
        local_constrained_configuration = dict()
        for valid_neighbor in  [x for x in self.gr.neighbors(n) if x in configuration[x.NAME] ]:
            try:
                local_constrained_configuration[valid_neighbor.NAME] += [valid_neighbor]
            except KeyError:
                local_constrained_configuration[valid_neighbor.NAME] = [valid_neighbor]

        if len(local_constrained_configuration) < self.gr.node[n]['ndep']:
            raise ConfigurationImpossible

        for variable in local_constrained_configuration:
            configuration[variable] = local_constrained_configuration[variable]
        
        return configuration

    def _constraint_next(self, variables, unconstrained_configuration):
        assert type(unconstrained_configuration) == dict
        
        if len (variables) > 0:
            cluster = variables[0]

            alternatives = unconstrained_configuration[cluster]
            alternatives.sort(reverse = True)
            for alternative in alternatives:
                try:
                    constrained = unconstrained_configuration
                    constrained[cluster] = [alternative]

                    constrained= self._local_constraint(alternative, constrained)
                    for sub_configuration in self._constraint_next(variables[1:], constrained): 
                        yield (alternative,) + sub_configuration

                except ConfigurationImpossible:
                    pass
        else:
            yield ()
                
    def constraint(self):
        alternative_count = 0
        for config in self._constraint_next(list(self.clusters.keys()), self.clusters):
            print (config)
            alternative_count += 1


            gr_config = self.gr.copy()
            for n in [n for n in gr_config.nodes() if n not in config]:
                gr_config.node[n]['pruned'] = True
                
            yield gr_config
            
        if alternative_count == 0:
            raise ConfigurationImpossible