from espresso import pmi
import _espresso
import espresso
from espresso.esutil import cxxinit

class FixedTripleListLocal(_espresso.FixedTripleList):
    'The (local) fixed triple list.'

    def __init__(self, storage):
        'Local construction of a fixed triple list'
        cxxinit(self, _espresso.FixedTripleList, storage)

    def add(self, pid1, pid2, pid3):
        'add triple to fixed triple list'
        return self.cxxclass.add(self, pid1, pid2, pid3)

    def addTriples(self, triplelist):
        """
        Each processor takes the broadcasted triplelist and
        adds those triples whose first particle is owned by
        this processor.
        """

        for triple in triplelist:
           pid1, pid2, pid3 = triple
           self.cxxclass.add(self, pid1, pid2, pid3)

if pmi.isController:
    class FixedTripleList(object):
        __metaclass__ = pmi.Proxy
        pmiproxydefs = dict(
            cls = 'espresso.FixedTripleListLocal',
            localcall = [ "add" ],
            pmicall = [ "addTriples" ]
            )
