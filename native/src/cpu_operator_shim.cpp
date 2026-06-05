#include "apc_runtime.hpp"

namespace apc {

NativeOperatorRequest make_probe_operator_request() {
  return NativeOperatorRequest{
      native_host_bridge_schema(),
      "native_cpu_probe",
      "binary_milp",
      "cpu",
      "state.candidate_major",
  };
}

NativeOperatorResult make_probe_operator_result() {
  return NativeOperatorResult{
      native_host_bridge_schema(),
      "native_cpu_probe",
      RuntimeStatus::implemented,
      empty_runtime_timing(),
      "operator_call.probe",
  };
}

OperatorCallRecord make_probe_operator_call_record() {
  return OperatorCallRecord{
      "native_cpu_probe",
      "cpu",
      RuntimeStatus::implemented,
      empty_runtime_timing(),
      "state.candidate_major",
      "operator_call.probe",
      "native_cpu_probe",
  };
}

NativeHostBridgeRecord make_probe_host_bridge_record() {
  return NativeHostBridgeRecord{
      native_host_bridge_schema(),
      make_probe_operator_request(),
      make_probe_operator_result(),
      make_probe_operator_call_record(),
  };
}

RuntimeStatus native_probe_status() {
  return RuntimeStatus::implemented;
}

}  // namespace apc
