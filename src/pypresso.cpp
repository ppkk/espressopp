/*
 This file contains the main routine for the embedded python
 interpreter version of ESPResSo. 
*/
#include "acconfig.hpp"
#include "espresso_common.hpp"
#include "python.hpp"
#include <iostream>

using namespace std;
using namespace boost;

/* The boostmpi sources do not declare init_boostmpi() in any header
   file, as it is a function that should usually be called when the
   module is loaded by Python. However, for linking it in, we need it,
   so, declare it here. The signature and name are known from the
   Python-API requirements.
*/
extern "C" {
  void init_boostmpi();
}

/** minimalistic ESPResSo module initialization,
    for use with the static initialization */
BOOST_PYTHON_MODULE(_espresso)
{
  espresso::registerPython();
}

/** On the controller, just adds the espresso library to python's
    builtin set of libraries and starts python.
    On the slaves, just starts PMI.
*/
int main(int argc, char **argv)
{
  int exitstate = 0;

  initMPI(argc, argv);

  if (PyImport_AppendInittab(const_cast<char *>("_espresso"), 
			     init_espresso) == -1) {
    cerr << "Could not add the ESPResSo module _espresso to python's list of preloaded modules."
	 << endl;
    exit(-1);
  }

// #ifndef BOOST_MPI_PYTHON_EXT
//   if (PyImport_AppendInittab(const_cast<char *>("_boostmpi"), 
// 			     init_boostmpi) == -1) {
//     cerr << "Could not add the builtin module _boostmpi to python's list of preloaded modules."
// 	 << endl;
//     exit(-1);
//   }

// #endif

  Py_Initialize();

  // fire up python
  exitstate = Py_Main(argc, argv);

  finalizeMPI();

  return exitstate;
}
