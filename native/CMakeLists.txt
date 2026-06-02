cmake_minimum_required(VERSION 3.18)

project(apc_native_host LANGUAGES CXX)

option(APC_ENABLE_NATIVE_HOST "Enable APC native host interface target" ON)

if(NOT APC_ENABLE_NATIVE_HOST)
  message(STATUS "APC native host runtime disabled")
  return()
endif()

add_library(apc_native_host STATIC src/cpu_operator_shim.cpp)
target_include_directories(
  apc_native_host
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_compile_features(apc_native_host PUBLIC cxx_std_17)

message(STATUS "APC native host runtime configured")
