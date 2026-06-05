#pragma once

// Public C++ host ABI for APC runtime evidence records.
//
// This header mirrors the Python runtime contract, operator call ledger, and
// runtime status code records. It is intentionally small and does not execute
// solver logic.

#include <cstdint>
#include <string_view>

namespace apc {

enum class RuntimeStatus : std::int32_t {
  implemented = 0,
  planned = 1,
  skipped = 2,
  failed = 3,
  unavailable = 4,
};

struct RuntimeTiming {
  double kernel_time_s;
  double copy_time_s;
  double layout_conversion_time_s;
  double end_to_end_time_s;
};

struct OperatorCallRecord {
  std::string_view step_name;
  std::string_view backend;
  RuntimeStatus status;
  RuntimeTiming timing;
  std::string_view inputs;
  std::string_view outputs;
  std::string_view operator_name;
};

struct NativeOperatorRequest {
  std::string_view schema;
  std::string_view operator_name;
  std::string_view problem_family;
  std::string_view backend;
  std::string_view inputs;
};

struct NativeOperatorResult {
  std::string_view schema;
  std::string_view operator_name;
  RuntimeStatus status;
  RuntimeTiming timing;
  std::string_view outputs;
};

struct NativeHostBridgeRecord {
  std::string_view schema;
  NativeOperatorRequest request;
  NativeOperatorResult result;
  OperatorCallRecord call;
};

constexpr std::string_view runtime_status_code(RuntimeStatus status) {
  switch (status) {
    case RuntimeStatus::implemented:
      return "implemented";
    case RuntimeStatus::planned:
      return "planned";
    case RuntimeStatus::skipped:
      return "skipped";
    case RuntimeStatus::failed:
      return "failed";
    case RuntimeStatus::unavailable:
      return "unavailable";
  }
  return "failed";
}

constexpr std::string_view runtime_contract_schema() {
  return "apc.runtime_execution_contract.v1";
}

constexpr std::string_view operator_call_ledger_schema() {
  return "apc.operator_call_ledger.v1";
}

constexpr std::string_view runtime_status_codes_schema() {
  return "apc.runtime_status_codes.v1";
}

constexpr std::string_view native_host_bridge_schema() {
  return "apc.native_host_bridge.v1";
}

constexpr RuntimeTiming empty_runtime_timing() {
  return RuntimeTiming{
      0.0,
      0.0,
      0.0,
      0.0,
  };
}

NativeOperatorRequest make_probe_operator_request();

NativeOperatorResult make_probe_operator_result();

NativeHostBridgeRecord make_probe_host_bridge_record();

OperatorCallRecord make_probe_operator_call_record();

RuntimeStatus native_probe_status();

}  // namespace apc
