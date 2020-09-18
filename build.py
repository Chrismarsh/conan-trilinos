from cpt.packager import ConanMultiPackager
from collections import defaultdict
import platform
if __name__ == "__main__":

    command=""
    if platform.system()== "Linux":
        command = "sudo apt-get -qq install -y libblas-dev liblapack-dev" #sudo apt-get -qq update && 

    
    builder = ConanMultiPackager(cppstds=[14],
                                archs=["x86_64"],
                                build_types=["Release"],
                                docker_entry_script=command)
                              
    builder.add_common_builds(pure_c=False,shared_option_name='trilinos:shared')

    builder.remove_build_if(lambda build: build.settings["compiler.libcxx"] == "libstdc++")

    named_builds = defaultdict(list)
    for settings, options, env_vars, build_requires, reference in builder.items:

        shared="shared"

        if not options['trilinos:shared']:
            shared = "static" 
      
        named_builds[settings['compiler'] +"_"+shared].append([settings, options, env_vars, build_requires, reference])

    builder.named_builds = named_builds

    builder.run()

