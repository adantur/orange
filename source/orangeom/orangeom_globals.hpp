#ifndef __ORANGEOM_GLOBALS
#define __ORANGEOM_GLOBALS

#include "garbage.hpp"

#ifdef _MSC_VER
    #ifdef ORANGEOM_EXPORTS
        #define ORANGEOM_API __declspec(dllexport)
        #define EXPIMP_TEMPLATE
    #else
        #define ORANGEOM_API __declspec(dllimport)
        #define EXPIMP_TEMPLATE extern
    
        #ifdef _DEBUG
            #pragma comment(lib, "orange_d.lib")
        #else
            #pragma comment(lib, "orange.lib")
        #endif
    #endif
#else
    #define ORANGEOM_API
    #define EXPIMP_TEMPLATE
#endif

#define OMWRAPPER(x) BASIC_WRAPPER(x, ORANGENE_API)
#define OMVWRAPPER(x) BASIC_VWRAPPER(x, ORANGENE_API)


#include "../pyxtract/pyxtract_macros.hpp"

#define PyTRY try {

#define PYNULL ((PyObject *)NULL)
#define PyCATCH   PyCATCH_r(PYNULL)
#define PyCATCH_1 PyCATCH_r(-1)

#define PyCATCH_r(r) \
  } \
catch (pyexception err)   { err.restore(); return r; } \
catch (mlexception err) { PYERROR(PyExc_OrangeKernel, err.what(), r); }

#endif
