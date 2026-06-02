cmake_minimum_required(VERSION 3.22)

project(apc_cuda_runtime LANGUAGES CXX)

option(APC_ENABLE_CUDA "Build APC CUDA runtime kernels" OFF)

add_library(apc_cuda_headers INTERFACE)
target_include_directories(
  apc_cuda_headers
  INTERFACE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

if(NOT APC_ENABLE_CUDA)
  message(STATUS "APC CUDA runtime disabled; configure with -DAPC_ENABLE_CUDA=ON when nvcc is available.")
  return()
endif()

include(CheckLanguage)
check_language(CUDA)
if(NOT CMAKE_CUDA_COMPILER)
  message(FATAL_ERROR "APC_ENABLE_CUDA=ON requires a CUDA compiler such as nvcc.")
endif()

enable_language(CUDA)

add_library(
  apc_cuda_runtime
  STATIC
    src/linear_csr_eval.cu
    src/violation_reduce.cu
    src/projection.cu
    src/clause_eval.cu
)
target_link_libraries(apc_cuda_runtime PUBLIC apc_cuda_headers)
target_compile_features(apc_cuda_runtime PUBLIC cxx_std_17)
set_target_properties(
  apc_cuda_runtime
  PROPERTIES
    CUDA_STANDARD 17
    CUDA_STANDARD_REQUIRED ON
    POSITION_INDEPENDENT_CODE ON
)
