cmake_minimum_required(VERSION 3.20)
project(competitive_programming_selected LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
option(ENABLE_SANITIZERS "Enable address/undefined-behaviour checks (GCC/Clang)" OFF)

file(GLOB SOLUTIONS CONFIGURE_DEPENDS "solutions/*.cpp")
foreach(SOLUTION IN LISTS SOLUTIONS)
    get_filename_component(TARGET_NAME "${SOLUTION}" NAME_WE)
    add_executable("${TARGET_NAME}" "${SOLUTION}")
    if(MSVC)
        target_compile_options("${TARGET_NAME}" PRIVATE /W4)
    else()
        target_compile_options("${TARGET_NAME}" PRIVATE -Wall -Wextra -pedantic)
        if(ENABLE_SANITIZERS)
            target_compile_options("${TARGET_NAME}" PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
            target_link_options("${TARGET_NAME}" PRIVATE -fsanitize=address,undefined)
        endif()
    endif()
endforeach()

include(CTest)
if(BUILD_TESTING)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    add_test(NAME differential COMMAND "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/check_solutions.py"
        --bin-dir "$<TARGET_FILE_DIR:connected_components>")
endif()

