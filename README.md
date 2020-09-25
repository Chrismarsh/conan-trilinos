## Package Status

[![Build Status](https://travis-ci.com/Chrismarsh/conan-trilinos.svg?branch=master)](https://travis-ci.com/Chrismarsh/conan-trilinos)

## General Information

Because of the tuned nature of BLAS and LAPACK libraries, only system BLAS and LAPACK are used in compilation.

### Intel MKL

To build against the Intel Math Kernel Library set the env var `$MKLROOT` to point to the root of the mkl install. On x86_64 platforms this will include the `/lib/intel64` part. 

### OpenBLAS

Set the conan option `-o trilinos:with_openblas=True` to change the link library name to `openblas`. This may only be useful on some systems. E.g., homebrew openblas has a lblas symlink.

### Custom BLAS location

The trilinos dependencies look for the BLAS libraries in a standard location. On HPC machines this will almost certainly fail, so the location of the library direction may be set via the env var `$BLASROOT`. LAPACK search will be set to the same path.  
