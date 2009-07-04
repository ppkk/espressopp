#######################################################
#
# Testing the decomposer
#

from espresso import pmi

if __name__ == 'espresso.pmi':
    from espresso import pmi
    from espresso.particles import PythonComputerLocal
    import sys

    # tag particles in a small sphere around (0,0,0) as demonstration
    class ParticleTesterLocal(PythonComputerLocal):
        def __init__(self, _position, _tag):
            PythonComputerLocal.__init__(self)
            self.position = _position
            self.tag = _tag

        def __apply__(self, pid):
            pos = self.position[pid]
            if pos*pos < 0.5:
                self.tag[pid] = 1
            else:
                self.tag[pid] = 0

    # write out tagged particles
    class ParticleWriterLocal(PythonComputerLocal):
        def __init__(self, _property, _tag):
            PythonComputerLocal.__init__(self)
            self.property = _property
            self.tag = _tag

        def prepare(self, storage) :
            self.total = 0
            self.sphere = 0

        def __apply__(self, pid) :
            self.total += 1
            if self.tag[pid]:
                print("%d %d %s" % (mpi.rank, pid, self.property[pid]))
                self.sphere +=1

        def finalize(self) :
            return mpi.world.reduce((self.sphere, self.total), lambda x,y : (x[0]+y[0], x[1]+y[1]), pmi.CONTROLLER)

else:

    pmi.execfile_(__file__)

    from espresso import boostmpi as mpi
    from espresso import Real3D, Real3DProperty
    from espresso.decomposition import SingleNode
    import random

    decomposer = SingleNode(mpi.size-1)
    pos = decomposer.createProperty("Real3D")

    for count in range(0,100):
        decomposer.addParticle(count)
        pos[count] = Real3D(random.random(), random.random(), random.random())

    # add property a posteriori
    tag = decomposer.createProperty("Integer")

    #tag particles
    # TBD: To create a PMI object referring to other PMI objects, we need to access
    # the PMI local object. Will there be a general rule for that? Like it is always
    # called "local"?
    decomposer.foreach(pmi.create("ParticleTesterLocal", pos.local, tag.local))

    # and print tagged ones
    count = decomposer.foreach(pmi.create("ParticleWriterLocal", pos.local, tag.local))
    print("printed %d out of %d particles" % count)