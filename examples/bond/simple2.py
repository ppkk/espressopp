#!/usr/bin/env python

###########################################################################
#                                                                         #
#  Example script for LJ and FENE for 2 trimers                           #
#                                                                         #
###########################################################################

import sys
import espresso
import MPI
import math
import logging

from espresso import Real3D, Int3D

size = (10.0, 10.0, 10.0)
numParticles = 6
cutoff = 2.5
ljSigma = 1.0
ljEpsilon = 1.0
skin = 0.3

# compute the number of cells on each node
def calcNumberCells(size, nodes, cutoff):
  ncells = 1
  while size / (ncells * nodes) >= (cutoff + skin):
     ncells = ncells + 1
  return ncells - 1

system = espresso.System()
system.rng = espresso.esutil.RNG()
system.bc = espresso.bc.OrthorhombicBC(system.rng, size)
system.skin = skin
comm = MPI.COMM_WORLD

nodeGrid = Int3D(1, 1, comm.size)
cellGrid = Int3D(
  calcNumberCells(size[0], nodeGrid[0], cutoff),
  calcNumberCells(size[1], nodeGrid[1], cutoff),
  calcNumberCells(size[2], nodeGrid[2], cutoff)
  )

print 'NodeGrid = %s' % (nodeGrid,)
print 'CellGrid = %s' % (cellGrid,)

system.storage = espresso.storage.DomainDecomposition(system, comm, nodeGrid, cellGrid)

# chain 1
system.storage.addParticle(0, Real3D(5.0, 5.0, 5.0))
system.storage.addParticle(1, Real3D(5.9, 5.0, 5.0))
system.storage.addParticle(2, Real3D(6.6, 5.5, 5.1))

# chain 2
system.storage.addParticle(3, Real3D(5.0, 5.0, 6.0))
system.storage.addParticle(4, Real3D(5.9, 5.0, 6.0))
system.storage.addParticle(5, Real3D(6.6, 5.5, 6.1))

system.storage.decompose()

# FENE with FixedPair list
fpl = espresso.FixedPairList(system.storage)
pairs = [(0, 1), (1, 2), (3, 4), (4, 5)]
fpl.addBonds(pairs)
potFENE = espresso.interaction.FENE(K=30.0, r0=0.0, rMax=1.5)
interFENE = espresso.interaction.FixedPairListFENE(fpl)
interFENE.setPotential(type1 = 0, type2 = 0, potential = potFENE)
system.addInteraction(interFENE)

# Cosine with FixedTriple list
ftl = espresso.FixedPairList(system.storage)
pairs = [(0, 1), (1, 2), (3, 4), (4, 5)]
ftl.addBonds(pairs)

# Lennard-Jones with Verlet list
vl = espresso.VerletList(system, cutoff = cutoff + system.skin)
potLJ = espresso.interaction.LennardJones(1.0, 1.0, cutoff = cutoff, shift=False)
interLJ = espresso.interaction.VerletListLennardJones(vl)
interLJ.setPotential(type1 = 0, type2 = 0, potential = potLJ)
system.addInteraction(interLJ)

# integrator
integrator = espresso.integrator.VelocityVerlet(system)
integrator.dt = 0.01

# analysis
temp = espresso.analysis.Temperature(system)
press = espresso.analysis.Pressure(system)
pressTensor = espresso.analysis.PressureTensor(system)

temperature = temp.compute()
p = press.compute()
pij = pressTensor.compute()
Ek = 0.5 * temperature * (3 * numParticles)
Ep_LJ = interLJ.computeEnergy()
Ep_FENE = interFENE.computeEnergy()

print 'E_total = ', Ek + Ep_LJ + Ep_FENE
print 'Ep_LJ = ', Ep_LJ
print 'Ep_FENE = ', Ep_FENE
print 'Ek = ', Ek
print 'T = ', temperature
print 'P = ', p

integrator.run(100)

temperature = temp.compute()
p = press.compute()
pij = pressTensor.compute()
Ek = 0.5 * temperature * (3 * numParticles)
Ep_LJ = interLJ.computeEnergy()
Ep_FENE = interFENE.computeEnergy()

print 'E_total = ', Ek + Ep_LJ + Ep_FENE
print 'Ep_LJ = ', Ep_LJ
print 'Ep_FENE = ', Ep_FENE
print 'Ek = ', Ek
print 'T = ', temperature
print 'P = ', p
