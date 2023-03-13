#
# Copyright 2020 Roche Sequencing Solutions, Inc.
#
# Author(s) Name: Suresh Agarwal
#
# Filename: CMakeLists.txt
#
# Description: Cmake file to build the publisher tool.
#

add_executable(NSCEServer NSCEServer.cpp PhysMem.cpp)
target_link_libraries(NSCEServer bus_lib logger_lib util_lib ${CPPREST_LIB} Threads::Threads)
set_target_properties(NSCEServer PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")



