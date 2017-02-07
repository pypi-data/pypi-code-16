from automata import Automaton
from sage.graphs.digraph import DiGraph
import os
from sage.sets.finite_set_maps import FiniteSetMaps
from sage.misc.cachefunc import cached_method

class monoidElement(tuple):
    def __repr__(self):
        s = ""
        for x in self:
            s += str(x)
        if s == "":
            return "1"
        else: 
            return s    
    def __add__(self,other):
        r = list()
        for x in self:
            r.append(x)
        for y in other:
            r.append(y)                    
        return monoidElement(r)
    def __getslice__(self,i,j):
        return monoidElement(tuple(self).__getslice__(i,j))
def power_set(E):
    if len(E) == 0:
        return [frozenset()]
    x = E.pop()
    l = power_set(E)
    l2 = []
    for U in l:
        l2.append(U.union([x]))
    return l+l2
def semigroup_closure(E):
    complete = False
    while not complete:
        complete = True
        F = E.copy()
        for x in F:
            for y in F:
                if x*y not in E:
                    E.add(x*y)
                    complete = False

def draw_box(box):
    s = '\\begin{tabular}{|'
    for i in range(len(box[0])):
        s = s+'c|'
    s = s + '}\n\\hline\n'
    for x in box:
        s =  s + '\n'
        l = list(x)
        s = s + '$'+str(l.pop())
        while len(l) > 0:
            s = s+'$&$'+str(l.pop())
        s = s+'$\\\\\n\\hline\n'   
    s = s.replace("['","")
    s = s.replace("']","")
    s = s.replace("'","")
   
    return s+'\\end{tabular}'
                           
def draw_box_dot(box,idempotents,colors_list=False,):
    s = '<<table border="1" cellborder="1" CELLSPACING="0" cellpadding="4">'
    for L in box:
        #uns = u.replace("*","")
        s = s + "<tr>"
        for H in L:
            if not colors_list:     
                s = s + "<td>"
            else:
                s = s + "<td bgcolor="+colors_list[H[0]]+">"        
            for a in H:
                if a in idempotents:
                    s = s + str(a) +"*,"
                else:
                    s = s + str(a) +","

            s = s[0:len(s)-1] + "</td>"
            #uns = u.replace("*","")              
        s = s+"</tr>"
    s = s + '</table>>' 
    return s                        

class TransitionSemiGroup(object):
    r"""
    Return the transition semigroup of a deterministic automaton.

    INPUT:

    - ``automaton`` -- deterministic automaton

    OUTPUT:

        Transition semigroup

    EXAMPLES::
    
        sage: from pysemigroup import Automaton, TransitionSemiGroup  
        sage: d = {(0, 'a'): [1], (1, 'a'): [0]}
        sage: A = Automaton(d,[0],[1])
        sage: S = TransitionSemiGroup(A)
        sage: S
        Transition SemiGroup of Automaton of 2 states

    """
    def __init__(self, automaton, monoid=True,compute=False, max_size= 0):
        r"""
        EXAMPLES::
        
            sage: from pysemigroup import Automaton, TransitionSemiGroup  
            sage: d = {(0, 'a'): [1], (1, 'a'): [0]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S
            Transition SemiGroup of Automaton of 2 states
        """
        if not isinstance(automaton, Automaton):
            raise TypeError('input(%s) must be an automaton' % automaton)
        if not automaton.is_deterministic() :
            raise ValueError('The automaton must be deterministic')
        self._monoid = monoid
        self._compute = compute
        self._generators = [monoidElement(x) for x in automaton._alphabet]      
        d = {}
        for x in automaton._transitions:
            d[(x[0],monoidElement(x[1]))] = automaton._transitions[x]                   
        self._automaton = Automaton(d,automaton._initial_states,automaton._final_states)         
        if compute:
            l = self.elements(max_size=max_size)            
    def __repr__(self):
        r"""
        EXAMPLES::
        
            sage: from pysemigroup import Automaton, TransitionSemiGroup          
            sage: d = {(0, 'a'): [1], (1, 'a'): [0]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S
            Transition SemiGroup of Automaton of 2 states
        """
        return "Transition SemiGroup of %s" % self._automaton

    @cached_method
    def graphviz_string(self, arrow=True,verbose=False,unfold=True,colors_list=False,new=True):
        r"""  
        Return graphviz eggbox representation of self. Set arrow to False to delete the arrow.
        INPUT :
        -  ``self`` -  Automaton        
        -  ``arrow`` -  boolean
        -  ``verbose`` -  boolean

        OUTPUT:

        string 

        EXAMPLES::
            sage: from pysemigroup import Automaton, TransitionSemiGroup
                    
        """

        #from sage.plot.colors import rainbow
        #col = rainbow(len(colors_list))
        #col_dic = {}
        
        #for x in colors_list:
        #      for y in x:            
        if verbose:
            print "computing box diagramm ..."
       
        box = self.box_representation(verbose=verbose)        
        idempotents = self.idempotents()
        if verbose:
            print "done."
        repre = set(box) 
        Gcal =  DiGraph(self.cayley_graph(loop=False, orientation="left_right"))  
        if verbose:
            edge_nb = str(len(Gcal.edges()))
            print "computing global structure ..."
            count = 0 
        for x in repre:
            if verbose:
                count = count+1
                print str(count)+"/"+str(edge_nb)
                sys.stdout.write("\033[F")
            Jx = set(self.J_class_of_element(x))
            Jx.remove(x)    
            Lx = [x]
            Lx.extend(Jx)            
            Gcal.merge_vertices(Lx)
        if verbose:
            print "done."

        Edge = []
        graph_viz = 'digraph {node [shape= none] \n'
        for x in repre:
            if x == '' or x == ():
                rx = '"1"'
            else:
                rx = '"'+str(x)+'"'
            if unfold:
               graph_viz = graph_viz + rx + ' [label='+draw_box_dot(box[x],idempotents,colors_list=colors_list)+'];\n'
            else:
               graph_viz = graph_viz + rx + ' [label='+rx+',shape="rectangle"];\n'

        if not arrow:         
            graph_viz = graph_viz + 'edge [style="invis"]\n'            
        if verbose:
            print "computing successor edges ..."
            count = 0
            loop_ln = len(repre)^2
        for x in repre:        
            for y in repre:                
                if (x,y)  in Gcal.edges(labels=False):      
                    if x == '' or x == ():
                        rx = '1'
                    else:
                        rx = str(x)
                    if y == '' or y == ():
                        ry = '1'
                    else:
                        ry = str(y)
                    graph_viz = graph_viz+'"'+rx+'"->"'+ry+'";\n'
        return graph_viz + '}'    


    def __call__(self,word):
        r"""
        Return the representent of word in the semigroup
        
        EXAMPLES::

            sage: from pysemigroup import Automaton, TransitionSemiGroup                      
            sage: d = {(0, 'a'): [2], (0, 'b'): [1], (1, 'a'): [0],  (1, 'b'): [2], (2, 'a'): [2], (2, 'b'): [2]}
            sage: A = Automaton(d,[1],[1])            
            sage: S = TransitionSemiGroup(A) 
            sage: S("abaaa")                   
            aa

        """
        return self.representent(word)        

    def __len__(self):
        r"""
        
        EXAMPLE::
            
        """
        return len(self.elements())        
    def length(self,maxsize=0):
        r"""
        
        EXAMPLE::
            
        """
        E = self.elements(maxsize=maxsize)
        if E == False:
            return maxsize+1
        return len(E)  

    def __iter__(self):
        r"""
        Return an iterator of the elements of the semigroup.        
        
        EXAMPLES::
        
            sage: from pysemigroup import Automaton, TransitionSemiGroup          
            sage: d = {(0, 'a'): [2], (0, 'b'): [1], (1, 'a'): [0],  (1, 'b'): [2], (2, 'a'): [2], (2, 'b'): [2]}
            sage: A = Automaton(d,[1],[1])            
            sage: S = TransitionSemiGroup(A)                   
            sage: it = iter(S)
            sage: sorted(it)
            [1, a, aa, ab, b, ba]
        """
        for x in self.elements():
            yield x
            
        
    
    @cached_method
    def _compute_semigroup(self, verbose=False):
        if not self._compute:
            E = self.elements(verbose=verbose)
        
    @cached_method
    def elements(self, maxsize= 0, verbose=False):
        r"""
        Compute the transition semigroup of the automaton
        
        INPUT :
        
        -  ``verbose`` - boolean

        EXAMPLES::

            sage: from pysemigroup import Automaton, TransitionSemiGroup          
            sage: d = {(0, 'a'): [1], (1, 'a'): [0]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S.elements()
            frozenset({1, a})

        """      
        A = self._generators
        Aut = self._automaton
        Sg = []
        Rep = {}
        Rep_rv = {}
        letter_quot = {}        
        F =  FiniteSetMaps(Aut._states)
        for x in A:
            d = {}
            for y in Aut._states:
                d[y] = Aut._transitions[(y,x)][0]
            fctx = F.from_dict(d)            
            if fctx not in Sg:
                Rep[fctx] = x
                Rep_rv[x] = fctx
                Sg.append(fctx)                     
            else:
                letter_quot[x] = fctx
        Gene = list(Sg)
        last = list(Sg)                        
        
        if self._monoid:
            d = {}
            for y in Aut._states:
                    d[y] = y
            ident = F.from_dict(d)
            
            if ident not in Sg:
                Rep[ident] = monoidElement("")
                Rep_rv[monoidElement("")] = ident
                Sg.append(ident)        
        count = 0
        while len(last)>0:
            old = list(last)
            last = []
            count = count + 1  
            if (maxsize>0) and (len(Sg)>maxsize):
                return False
            for u in old:
                for v in Gene:
                    v_u = v*u
                    Ru = Rep[u]
                    Rv = Rep[v]
                    if  v_u not in Sg:
                        if verbose:
                            print "new element "+str(Ru+Rv)+"no: "+str(len(Sg))
                            sys.stdout.write("\033[F")
                        Sg.append(v_u)
                        last.append(v_u)
                        Ruv = Ru+Rv
                        Rep[v_u] = Ruv
                        Rep_rv[Ruv] = v_u
        self._Sg = Sg
        self._Representations = Rep
        self._Representations_rev = Rep_rv
        self._compute = True
        self._letter_quot=letter_quot
        return frozenset(self._Representations_rev)
    def get_identity(self):
        try: 
            return self._identity
        except:
            k = self.elements()
            l = list(self._Representations)
            for x in l:
                if x.is_one():
                    self._identity = self._Representations[x]
                    return self._identity
            raise ValueError("No indentity in this semigroup")
    @cached_method    
    def representent(self, v):
        r"""
        Return a representent of the equivalence class of the word u in the transition semigroup
        p
        INPUT :
        
        - ``u``  - string or monoid element

        EXAMPLES::

            sage: from pysemigroup import Automaton, TransitionSemiGroup
            sage: d = {(0, 'a'): [1], (1, 'a'): [0]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S.representent('aaa')
            a
        """
        l = self.elements()        
        u = monoidElement(v)
        if u in self._Representations.values():
            return u
        else:        
            if len(u) == 0:
                return self.get_identity()  
            if len(u) == 1:
                if u in self._letter_quot:     
                    return self._Representations[self._letter_quot[u]]
                else:
                    raise TypeError("Words not defined in this alphabet")
                
            if len(u)%2 == 0:
                return self._Representations[self._Representations_rev[self.representent(u[len(u)/2:len(u)])]*self._Representations_rev[self.representent(u[0:len(u)/2])]] 
            else:
                return self._Representations[self._Representations_rev[self.representent(u[(len(u)-1)/2:len(u)])]*self._Representations_rev[self.representent(u[0:(len(u)-1)/2])]] 


    @cached_method
    def idempotents(self):
        r"""
        Return the idempotents of the semigroup

        EXAMPLES::

            sage: from pysemigroup import Automaton, TransitionSemiGroup  
            sage: d = {(0, 'a'): [1], (1, 'a'): [0]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S.idempotents()
            {1}

        """
        self._compute_semigroup()
        I = set()
        for u in self.elements():
            if self(u+u) == self(u):
                I.add(u)
        return I

    def _relabel_idempotent(self,u):
        if u in self.idempotents():
            return u
        else:
            return u
    @cached_method
    def cayley_graph(self, loop= True, label=True, orientation="right"):
        r"""
        Return the Cayley graph of the semigroup
        INPUT :
        
        - ``idempotent``  -- boolean -- if True, return a Digraph with idempotent mark with a star
        - ``orientation``  -- string --  value "left", "left_right", "right". 
        


        EXAMPLES::

            sage: from pysemigroup import Automaton, TransitionSemiGroup  
            sage: d = {(0, 'a'): [2], (0, 'b'): [1], (1, 'a'): [0],  (1, 'b'): [2], (2, 'a'): [2], (2, 'b'): [2]}
            sage: A = Automaton(d,[1],[1])            
            sage: S = TransitionSemiGroup(A)
            sage: G = S.cayley_graph()
            sage: G
            Looped multi-digraph on 6 vertices
        """
        d = {}
        A = self._generators
        if orientation in  ["right","left_right"]:
            for x in self:          
                d[x] = {}
                for c in A:
                    if self(x+c) in d[x]:
                        d[x][self(x+c)].append((c,"r"))
                    else :
                        d[x][self(x+c)]= [(c,"r")]
        if orientation in  ["left","left_right"]:
            for x in self:   
                if orientation == "left":       
                    d[x] = {}
                for c in A:
                    if self(c+x) in d[x]:
                        d[x][self(c+x)].append((c,"l"))
                    else :
                        d[x][self(c+x)] = [(c,"l")]


        G = DiGraph(d)  
        if not loop:
            G.allow_loops(False)
        if not label:
            G = DiGraph(list(set([(e[0],e[1]) for e in G.edges()])))
        return G         

    def cayley_graphviz_string(self,edge_label=True, orientation="left_right"):
        s = 'digraph {\n node [margin=0 shape="circle" ]\n'
        Elements = set(self)
        while (len(Elements) > 0):
            e = Elements.pop()
            if (orientation == "left"):
                E = self.L_class_of_element(e)
            elif (orientation == "right"):
                E = self.R_class_of_element(e)
            elif (orientation == "left_right"):
                E = self.J_class_of_element(e)
            else:
                raise ValueError("Orientation(={}) should be 'left', 'right', or 'left_right'".format(orientation))
            s = s + 'subgraph cluster'+str(e)+'{style=filled;\ncolor=black;\nfillcolor=azure;\n'        
            for x in E:
                if (x == ""):
                    s = s+'  "'+str(x)+'" [label="'+str(1)+'"'
                else:
                    s = s+'  "'+str(x)+'" [label="'+str(x)+'"'

                if x in self.idempotents():
                    s = s + ' fontcolor="red"'
                else:
                    s = s + ' fontcolor="blue"'
                s = s +'];\n'
            s = s + '}\n'
        for x in self:        
            for y in self:
                edge = []
                for a in self._generators:                    
                    if (orientation in ["right","left_right"]) and y == self(x+a):
                        edge.append("."+str(a))
                    if (orientation in ["left","left_right"]) and y == self(a+x):
                        edge.append(str(a)+".")
                    
                if len(edge)>0:
                    s = s+ '  "'+str(x)+'" -> "'+str(y)+'"['
                    if edge_label:
                        s = s + 'label="'+str(edge.pop())
                        while len(edge)>0:
                            s = s+ ','+str(edge.pop())
                        s = s + '",'
                    if y == x:
                        s =  s+ 'topath="loop above"'
                    s = s + '];\n'
        s = s+'}'    
        return s    

    
    def idempotent_power(self,u):
        r"""
        Return the idempotents power of the word u
        
        INPUT :

        -  ``u`` -  (word)

        EXAMPLES::

            sage: from pysemigroup import Automaton, TransitionSemiGroup
            sage: d = {(0, 'a'): [1], (1, 'a'): [0]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S.idempotent_power('a')
            1
        """
        self._compute_semigroup()
        if isinstance(u,str) or isinstance(u,tuple):
            f = self._Representations_rev[self.representent(u)]
            g = f
            while not (g.is_idempotent()) :
                g =  f * g
            return self._Representations[g]
        else:
            g = u
            while not (g.is_idempotent) :
                g = u * g 
            return g
    def _get_J_topological_sort(self):
        
        try :
            T = self._J_topological_sort
        except:
            T = self.cayley_graph(loop=False, label=False,orientation="left_right").strongly_connected_components_digraph().topological_sort()
            self._J_topological_sort = T
        return T
    def pop_J_maximal(self,E):  
        r"""
            Output the J-maximal element of E and delete it.         
        INPUT :
        -  ``E`` -  set 

        EXAMPLES::
            sage: from pysemigroup import Automaton, TransitionSemiGroup  
            sage: d = {(0, 'a'): [2], (0, 'b'): [1], (1, 'a'): [0],  (1, 'b'): [2], (2, 'a'): [2], (2, 'b'): [2]}
            sage: A = Automaton(d,[1],[1])  
            sage: S = TransitionSemiGroup(A)
            sage: E = set(S.elements())
            sage: S.pop_J_maximal(E)
            1

        """
        
        if len(E) == 0 or not E.issubset(self.elements()):
            return False
        T = self._get_J_topological_sort()
        for x in T:
            F = set(x).intersection(E)
            if len(F) > 0:
                return F.pop()
        return E.pop()  

    def is_sub_semigroup(self, S, verbose = False):
        r"""
        Return whether S is a sub semigroup of self.
        
        INPUT :

        -  ``S`` - iterable of words
        -  ``verbose`` - boolean 

        
        EXAMPLES::
            sage: from pysemigroup import Automaton, TransitionSemiGroup             
            sage: d = {(0, 'a'): [1], (1, 'a'): [0]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S.is_sub_semigroup(("a"))
            False
            sage: S.is_sub_semigroup(("aa"))
            False
            sage: S.is_sub_semigroup((""))
            True
        """
        for i in S:
            for j in S:
                if verbose:
                    print str((i,j))        
                if not self.representent(i+j) in set(S):
                    return False
        return True

    def sub_semigroup_generated(self, E, verbose=False):
        F = set(E)
        G = set()
        while len(F) > 0:
            if verbose:
                print "new element len:"+str(len(F))
                sys.stdout.write("\033[F")                                             
 
            G = G.union(F)
            F = set()
            for x in G:
                for y in G:
                    if  (not self(x+y) in G):
                        F.add(self(x+y))
        return G

    @cached_method
    def _stable(self, verbose=False):
        i = 1

        A = self._generators
        S = set([self.representent(a) for a in A])
        while not self.is_sub_semigroup(S):
            i = i + 1
            if verbose:
                print i
                print S
            T = set([])
            for u in S:
                for a in A:
                    T.add(self(u+a))
            S = T
        return (S,i)        
        
    @cached_method
    def stability_index(self, verbose=False):
        r"""
        Return the stablility index

        OUTPUT :
            
            integer s
        
        EXAMPLES::

            sage: from pysemigroup import Automaton, TransitionSemiGroup
            sage: A = RegularLanguage("(a*b)^x",['a','b']) # not tested
            sage: d = {(0, 'a'): [2], (0, 'b'): [1], (1, 'a'): [0], (1, 'b'): [2], (2, 'a'): [2], (2, 'b'): [2]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S.stability_index()
            2
        """

        return self._stable()[1]

        
    def stable_set(self, verbose=False):
        r"""
        Return the stable semigroup

        OUTPUT :
            
            tuple (i,S) 
        
        EXAMPLES::

            sage: from pysemigroup import Automaton, TransitionSemiGroup
            sage: A = RegularLanguage("(a*b)^x",['a','b']) # not tested
            sage: d = {(0, 'a'): [2], (0, 'b'): [1], (1, 'a'): [0], (1, 'b'): [2], (2, 'a'): [2], (2, 'b'): [2]}
            sage: A = Automaton(d,[0],[1])
            sage: S = TransitionSemiGroup(A)
            sage: S.stable_semigroup()
            Transition SemiGroup of Automaton of 4 states

        """
        return self._stable()[0]
    def stable_semigroup(self):
        S = self._stable()[0]
        S.add(monoidElement(""))
        d = {}
        for x in S:
            for y in S:
                d[(str(x),(str(y),))] = [str(self(x+y))]
        return TransitionSemiGroup(Automaton(d,[0],[0]))        
    def stabilized_automaton(self):
        r"""
        Return the automata recognizing the language enriched by modular counting
        """
        Aut = self._automaton
        d_old = Aut.s_transitions
        d = {}
        s = self.stability_index()
        A = Aut._alphabet
        States = Aut._states
        for a in A:
            for i in range(s):
                for x in States:
                    d[(x,(a,i))] = d_old[(x,a)]
        Enr_Aut = Automaton(d,Aut._initial_states,Aut._final_states)
        d = {}
        for a in A:
            for i in range(s):
                d[(i,(a,i))] = [(i+1)%s]
        Count_Aut = Automaton(d,[0],range(s))
        return Enr_Aut.intersection(Count_Aut).minimal_automaton()                                

    def J_class_of_element(self,x):
        xs = self.representent(x)
        G = self.cayley_graph(loop=False, orientation="left_right")
        return set(G.strongly_connected_component_containing_vertex(xs))

    def J_ideal_of_element(self,x):
        xs = self.representent(x)
        G = self.cayley_graph(loop=False, orientation="left_right").transitive_closure()
        return set(G.neighbors_out(x))
    
    def R_class_of_element(self,x):
        xs = self.representent(x)
        G = self.cayley_graph(loop=False, orientation="right")
        return set(G.strongly_connected_component_containing_vertex(xs))

    def L_class_of_element(self,x):
        xs = self.representent(x)
        G = self.cayley_graph( loop=False, orientation="left")       
        return set(G.strongly_connected_component_containing_vertex(xs))

    def H_class_of_element(self,x):
        return self.R_class_of_element(x).intersection(self.L_class_of_element(x))

    def is_element_neutral(self, x):
        E = self.elements()
        for y in E:
            if not self.representent(x+y) == y:
                return False
            if not self.representent(y+x) == y:
                return False
        return True

    
    def _sg_reverse(self,u,v):
        S = self
        G = S.cayley_graph(orientation="left_right")
        su = S(u)
        sv = S(v)
        l = G.shortest_path(u,v)
        if len(l) == 0:
            raise TypeError("no inverse")
        l.reverse()
        x = l.pop()
        w1 = monoidElement("")
        w2 = monoidElement("")    
        while len(l)>0:
            y = l.pop()
            a = G.edge_label(x,y)[0]
            if a[1] == "r":
                w1 = w1 + a[0]
            else:
                w2 = a[0] + w2 
       
            x = y
        return (w2,w1)                

    def newbox(self,x):
        if (x not in self):
            raise TypeError("unboxable element")
        else:
            shiftR = []
            shiftL = []
            box = {}       
            Jx = self.J_class_of_element(x)
            Lx = self.L_class_of_element(x)
            Rx = self.R_class_of_element(x)
            Idempotents = Jx.intersection(self.idempotents())
            cx = 0
            cy = 0
            if len(Idempotents) > 0:        
                x = Idempotents.pop()
                Lx = self.L_class_of_element(x)
                Rx = self.R_class_of_element(x)
                Idempotents = Idempotents.difference(self.R_class_of_element(x))
                Idempotents = Idempotents.difference(self.L_class_of_element(x))
                while len(Idempotents) > 0:
                    cx = cx + 1
                    cy = cy + 1
                    y = Idempotents.pop()
                    Idempotents = Idempotents.difference(self.R_class_of_element(y))
                    Idempotents = Idempotents.difference(self.L_class_of_element(y))
                    z = self._sg_reverse(x,y)

                    Lx = Lx.difference(self.H_class_of_element(self(z[0]+x)))
                    Rx = Rx.difference(self.H_class_of_element(self(x+z[1])))                
                    shiftR.append(z[1])
                    shiftL.append(z[0])
            while len(Lx) > 0:
                l = Lx.pop()
                cy = cy + 1
                Hl = self.H_class_of_element(l)
                Lx = Lx.difference(Hl)
                shiftL.append(self._sg_reverse(x,l)[0])
            while len(Rx) > 0:
                r = Rx.pop()
                cx = cx + 1
                Hr = self.H_class_of_element(r)
                Rx = Rx.difference(Hr)
                shiftR.append(self._sg_reverse(x,r)[1])
        for i in range(0,cx):
            for j in range(0,cy):
                sr = shiftR[i]
                sl = shiftL[j]
                y = self(sl+x+sr)
                box[(i,j)] = (y,self.H_class_of_element(y))
        box["width"] = cx
        box["height"] = cy
        return box

    def newbox_oldbox(self,x):
        nbox = self.newbox(x)
        obox = []
        for x in range(nbox["height"]):
            L = []
            for y in range(nbox["width"]):
                H = list(nbox[(y,x)][1])
                
                L.append(H)
            obox.append(L)
        return obox              
    def box_representation(self,verbose=False):
        E = set(self.elements())
        dic = {}
        box = {}
        if verbose:
            print "computing Jclass ..."
        while len(E)>0:
            x = self.pop_J_maximal(E)
            if verbose:
                    print "Dealing with "+str(x)
            
            Jclass = self.J_class_of_element(x)            
            box[x] = []
            E = E.difference(Jclass)
        for x in box:
            box[x] = self.newbox_oldbox(x)
        return box


    
    
    def view(self, arrow=True,verbose=False,unfold=True,new=True):
        from sage.misc.temporary_file import tmp_filename 
        from sage.misc.viewer import viewer
        file_dot = tmp_filename(".",".dot")
        file_gif = tmp_filename(".",".gif")
        f = file(file_dot,'w')
        f.write(self.graphviz_string(arrow=arrow,verbose=verbose,unfold=unfold,new=new))
        f.close()
        os.system('dot -Tgif %s -o %s; %s %s  2>/dev/null 1>/dev/null '%(file_dot,file_gif,viewer(),file_gif))

    def view_cayley(self,orientation="left_right",edge_label=True):
        from sage.misc.temporary_file import tmp_filename 
        from sage.misc.viewer import viewer

        file_dot = tmp_filename(".",".dot")
        file_gif = tmp_filename(".",".gif")
        f = file(file_dot,'w')
        f.write(self.cayley_graphviz_string(edge_label=edge_label,orientation=orientation))
        f.close()
        os.system('dot -Tgif %s -o %s; %s %s  2>/dev/null 1>/dev/null '%(file_dot,file_gif,viewer(),file_gif))
        
    def is_Ap(self,verbose=False):
        for e in self.idempotents():
            H = self.H_class_of_element(e)
            if len(H)>1:
                if verbose:
                    print "A non trivial H-class for element:"+str(e)
                return False
        return True        
    def is_J(self,verbose=False):
        for x in self:
            J = self.H_class_of_element(x)
            if len(J)>1:
                if verbose:
                    print "A non trivial J-class for element:"+str(x)
                return False
        return True        

    def is_Idempotent(self,verbose=False):
        Sg = set(self.elements())
        E = set(self.idempotents())
        if not (E == Sg) and verbose:        
            print str((Sg.difference(E)).pop())
        return E == Sg        

    def is_Commutative(self,verbose=False):
        for x in self:
            for y in self:
                if not (self(x+y) == self(y+x)):
                    if verbose:
                        print (x,y)
                    return False 
        return True
    
    def is_Jun(self,verbose=False):
        return is_Idempotent(verbose=verbose) and is_Commutative(verbose=verbose)
          

    def has_a_zero(self):
        G = self.cayley_graph(orientation="left_right")
        G.remove_loops()
        if len(G.sinks()) == 1:
            return True
        else:
            return False   
    def get_zero(self):
        G = self.cayley_graph(orientation="left_right")
        G.remove_loops()
        if len(G.sinks()) == 1:
            return G.sinks()[0] 
        else:
            raise ValueError("The semigroup must have a zero")
    
                    
    def to_gif(self,s):
        f = file(s+".dot",'w')
        f.write(self.graphviz_string())
        f.close()
        os.system('dot -Tgif %s -o %s; rm %s  2>/dev/null 1>/dev/null '%(s+".dot",s+".gif",s+".dot"))

