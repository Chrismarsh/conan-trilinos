from conans import ConanFile, CMake, tools
import os

class TrilinosConan(ConanFile):
    name = "trilinos"
    description = "The Trilinos scientific computing software stack"
    topics = ("conan", "trilinos", "scientific computing")
    url = "https://github.com/kevinrichardgreen/conan-trilinos"
    homepage = "https://trilinos.github.io/"
    license = "BSD/multi" # TODO: appropriate license tag... packages in Trilinos are variable

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "with_all_packages": [True, False],
        "with_belos": [True, False],
        "with_ifpack2": [True, False],
        "with_openmp": [True, False],
        "with_mpi": [True, False],
        "with_mkl": [True, False],
        "with_openblas": [True,False],

        "mkl_root": "ANY",
        "blas_root":"ANY"
    }
    default_options = {
        "shared": True,
        "with_all_packages": False,
        "with_belos": True,         # iterative solvers
        "with_ifpack2": True,       # preconditioners
        "with_openmp": True,
        "with_mpi": False,
        "with_mkl": False,
        "with_openblas":False,

        "mkl_root": None,
        "blas_root": None
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    # build_policy = 'always'
    requires = (
        "zlib/1.2.11"
    )

    def config_options(self):
        if self.settings.os not in ["Macos", "Linux"]:
            raise Exception("Unsupported System. This package currently only support Linux/Macos")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Trilinos-trilinos-release-%s" % self.version.replace(".","-")
        os.rename(extracted_dir, self._source_subfolder)

        if tools.os_info.is_macos and self.options.with_openmp:
            print('!!! Macos and OMP not supported, setting with_openmp=false')
            self.options.with_openmp = False

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.with_mkl:

            if self.options.mkl_root is None:
                self.output.error('If building against mkl, ensure -o mkl_root is set. For example, -o trilinos:mkl_root=/opt/imkl/2019.3.199/mkl/lib/intel64" ')
                raise Exception('mkl_root not set')

            # as per https://github.com/trilinos/Trilinos/blob/master/cmake/TPLs/FindTPLMKL.cmake#L116
            cmake.definitions["BLAS_LIBRARY_DIRS:FILEPATH"] =self.options.mkl_root 
            cmake.definitions["BLAS_LIBRARY_NAMES:STRING"] ="mkl_rt" 

            cmake.definitions["LAPACK_LIBRARY_DIRS:FILEPATH"] =self.options.mkl_root
            cmake.definitions["LAPACK_LIBRARY_NAMES:STRING"] ="mkl_rt" 
            
            cmake.definitions["TPL_ENABLE_MKL:BOOL"] ="ON" 
            cmake.definitions["MKL_LIBRARY_DIRS:FILEPATH"] =self.options.mkl_root
            cmake.definitions["MKL_LIBRARY_NAMES:STRING"] ="mkl_rt" 
            cmake.definitions["MKL_INCLUDE_DIRS:FILEPATH"] =self.options.mkl_root+"/../../include" 

        if self.options.with_openblas:
            cmake.definitions["BLAS_LIBRARY_NAMES:STRING"] ="openblas" 
            cmake.definitions["LAPACK_LIBRARY_NAMES:STRING"] ="openblas" 

        
        if self.options.blas_root:
            cmake.definitions["BLAS_LIBRARY_DIRS:FILEPATH"] = self.options.blas_root
            cmake.definitions["LAPACK_LIBRARY_DIRS:FILEPATH"] = self.options.blas_root

        if self.settings.compiler == 'apple-clang' and tools.Version(self.settings.compiler.version).major >= '12':
            self.output.info("apple-clang v12 detected")
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-Wno-implicit-function-declaration"
            cmake.definitions["CMAKE_C_FLAGS"] = "-Wno-implicit-function-declaration"


        cmake.definitions["Trilinos_ENABLE_Fortran"] = False
        cmake.definitions["Trilinos_ENABLE_TESTS"] = False

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared

        cmake.definitions["Trilinos_ENABLE_ALL_PACKAGES"] = self.options.with_all_packages

        cmake.definitions["Trilinos_ENABLE_Belos"] = self.options.with_belos
        cmake.definitions["Trilinos_ENABLE_Ifpack2"] = self.options.with_ifpack2

        cmake.definitions["Trilinos_ENABLE_OpenMP"] = self.options.with_openmp
        cmake.definitions["Trilinos_ENABLE_THREAD_SAFE"] = self.options.with_openmp

        cmake.definitions["TPL_ENABLE_MPI"] = self.options.with_mpi

        cmake.definitions["CMAKE_CXX_FLAGS"] ="-Wno-unused-result -Wno-deprecated-declarations"

        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
