#__author__    = "Sharath Maddineni"
#__email__     = "smaddineni@cct.lsu.edu"
#__copyright__ = "Copyright 2011, Sharath Maddineni"
#__license__   = "MIT"


[echo_hello]
executable = /bin/date
spmd_variation = single
number_of_processes = 1
arguments = 
#arguments = arg_1,arg_2,arg_3,arg_4
out_arg_value = arg_4_key
arg_1_key = -a
#default value
arg_1_value = 123
arg_2_key = -b
arg_2_value = True
arg_3_key = -c 
arg_4_key = p
env_variables = env_1,env_2
env_1 = "PATH"

[machine_1]
arg_3_value = "/path/to/file"
env_1_value = "/usr/bin/"

[machine_2]
arg_3_value = "/path/to/file"
env_1_value = "/usr/bin/"
