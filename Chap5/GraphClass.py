EPSILON = 0.001
def printDico(dico):
    for e in dico:
        print(e, ":", dico[e])

class Graph:
    def __init__(self, states, trans):
        """
        :param states: set of states
        :param trans: dictionary giving transitions
        :param start: set of beginings
        """
        self.states = states
        self.trans = trans
    
    def get_states(self):
        return self.states

    def add_state(self, state):
        """
        :param state: state to be added
        :return: 1 if state successfuly added, 0 otw
        """
        if state in self.states:
            print("Error while adding state: already present")
            return 0
        try: 
            self.states.add(state)
        except:
            print("Error while adding state: set error")
            return 0
        return 1

    def add_transition(self, source, label, target): 
        """
        :param source: source state
        :param label: label of the transition
        :param target: target state
        :return: 1 if transition successfuly added, 0 otw
        """
        if source not in self.states:
            print("Error while adding transition: source state not in states")
            return 0
        if target not in self.states:
            print("Error while adding transition: target state not in states")
            return 0

        # source is not a key of self.trans
        if source not in self.trans:
            self.trans[source] = {}
            self.trans[source][label]={target}
        # source is a key of self.trans
        else:
            # label is not a key of self.trans[source]
            if label not in self.trans[source]:
                self.trans[source][label]={target}
            # label is a key of self.trans[source]
            else:
                self.trans[source][label].add(target)
        return 1               

    def get_cost(self, source, target):
        if source not in self.states:
            raise Exception("Error while adding transition: source not in states")
            
        if target not in self.states:
            raise Exception("Error while adding transition: target not in states")
            
        # state1 is not a key of self.trans
        if source not in self.trans:
            return 0
        else:
            for label in self.trans[source]:
                if self.trans[source][label] == target:
                    return label
        return 0               
 
    def __str__(self):
        """ Overrides print function """
        res = "Display Graph\n"
        res += "Set of states: "+str(self.states) +"\n"
        res += "Transitions:"+"\n"
        for source in self.trans:
            for label in self.trans[source]:
                for target in self.trans[source][label]:
                    res += "Transition from "+str(source)+" to "+str(target)+" labelled by "+str(label)+"\n"
        return res

    def compute_next(self, X):
        """
        :param X: set of states
        :return: a set of states corresponding to one-step successors of X by reading sigma
        """
        res = set()
        for source in X:
            if source in self.trans:
                for label in self.trans[source]:
                    if label in self.trans[source]:
                        for target in self.trans[source][label]:
                            res.add(target)
        return res
    
        """
        :param n: Number of states to be added
        :return: 1 if state successfuly added, 0 otw
        """

    def removeNullDistance(self):
        res = {}
        for source in self.trans:
            res[source] = {}
            for label in self.trans[source]:
                if not(-EPSILON < label and label < EPSILON): 
                    res[source][label] = self.trans[source][label] 
        return replaceTrans(self, res)

# =============== CREATIONS ===============

def createBlankGraph():
    A = Graph(set(), {})
    print(A)
    return A

def replaceTrans(graph, dico):
    graph.trans = dico
    return graph

# =============== TEST ===============

