cmake_minimum_required(VERSION 3.20)
project(competitive_programming_selected LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

file(GLOB SOLUTIONS CONFIGURE_DEPENDS "solutions/*.cpp")
foreach(SOLUTION IN LISTS SOLUTIONS)
    get_filename_component(TARGET_NAME "${SOLUTION}" NAME_WE)
    add_executable("${TARGET_NAME}" "${SOLUTION}")
    if(MSVC)
        target_compile_options("${TARGET_NAME}" PRIVATE /W4)
    else()
        target_compile_options("${TARGET_NAME}" PRIVATE -Wall -Wextra -pedantic)
    endif()
endforeach()

