#include <cuda_runtime.h>

#include <cstdio>
#include <cstdlib>
#include <vector>

__global__ void project_binary_kernel(int* values, int count) {
  const int idx = blockIdx.x * blockDim.x + threadIdx.x;
  if (idx >= count) {
    return;
  }
  values[idx] = values[idx] >= 1 ? 1 : 0;
}

void fail(const char* label, cudaError_t err) {
  if (err != cudaSuccess) {
    std::fprintf(
        stderr,
        "{\"available\":false,\"reason\":\"%s: %s\"}\n",
        label,
        cudaGetErrorString(err));
    std::exit(1);
  }
}

int main(int argc, char** argv) {
  const int count = argc > 1 ? std::atoi(argv[1]) : 1024;
  if (count <= 0) {
    std::fprintf(stderr, "{\"available\":false,\"reason\":\"count must be positive\"}\n");
    return 1;
  }

  int device_count = 0;
  cudaError_t count_err = cudaGetDeviceCount(&device_count);
  if (count_err != cudaSuccess || device_count <= 0) {
    std::fprintf(
        stderr,
        "{\"available\":false,\"reason\":\"cuda device unavailable: %s\"}\n",
        cudaGetErrorString(count_err));
    return 1;
  }

  std::vector<int> host(count, 0);
  for (int i = 0; i < count; ++i) {
    host[i] = (i % 3) - 1;
  }

  int* device = nullptr;
  fail("cudaMalloc", cudaMalloc(&device, sizeof(int) * count));

  cudaEvent_t copy_start;
  cudaEvent_t copy_stop;
  cudaEvent_t kernel_start;
  cudaEvent_t kernel_stop;
  fail("cudaEventCreate", cudaEventCreate(&copy_start));
  fail("cudaEventCreate", cudaEventCreate(&copy_stop));
  fail("cudaEventCreate", cudaEventCreate(&kernel_start));
  fail("cudaEventCreate", cudaEventCreate(&kernel_stop));

  fail("copy event start", cudaEventRecord(copy_start));
  fail(
      "host to device copy",
      cudaMemcpy(device, host.data(), sizeof(int) * count, cudaMemcpyHostToDevice));
  fail("copy event stop", cudaEventRecord(copy_stop));
  fail("copy sync", cudaEventSynchronize(copy_stop));

  const int block = 256;
  const int grid = (count + block - 1) / block;
  fail("kernel event start", cudaEventRecord(kernel_start));
  project_binary_kernel<<<grid, block>>>(device, count);
  fail("kernel launch", cudaGetLastError());
  fail("kernel event stop", cudaEventRecord(kernel_stop));
  fail("kernel sync", cudaEventSynchronize(kernel_stop));

  fail(
      "device to host copy",
      cudaMemcpy(host.data(), device, sizeof(int) * count, cudaMemcpyDeviceToHost));

  float copy_ms = 0.0f;
  float kernel_ms = 0.0f;
  fail("copy elapsed", cudaEventElapsedTime(&copy_ms, copy_start, copy_stop));
  fail("kernel elapsed", cudaEventElapsedTime(&kernel_ms, kernel_start, kernel_stop));

  fail("cudaFree", cudaFree(device));
  fail("destroy copy start", cudaEventDestroy(copy_start));
  fail("destroy copy stop", cudaEventDestroy(copy_stop));
  fail("destroy kernel start", cudaEventDestroy(kernel_start));
  fail("destroy kernel stop", cudaEventDestroy(kernel_stop));

  std::printf(
      "{\"available\":true,\"count\":%d,\"copy_time_s\":%.9f,\"kernel_time_s\":%.9f}\n",
      count,
      static_cast<double>(copy_ms) / 1000.0,
      static_cast<double>(kernel_ms) / 1000.0);
  return 0;
}
