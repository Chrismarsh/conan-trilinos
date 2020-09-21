from conans import ConanFile, CMake, tools
import os

class TrilinosConan(ConanFile):
    name = "trilinos"
    version = "12.18.1"
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
        "with_mpi": [True, False]
    }
    default_options = {
        "shared": True,
        "with_all_packages": False,
        "with_belos": True,         # iterative solvers
        "with_ifpack2": True,       # preconditioners
        "with_openmp": True,
        "with_mpi": False
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
