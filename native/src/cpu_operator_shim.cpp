#include "apc_runtime.hpp"

namespace apc {

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

RuntimeStatus native_probe_status() {
  return RuntimeStatus::implemented;
}

}  // namespace apc
