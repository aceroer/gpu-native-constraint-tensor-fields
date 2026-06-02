#pragma once

// Minimal CUDA-side ABI sketch for the binary MILP repair example.
//
// This header mirrors the theory stack:
// L6 CTIR          -> APC_LinearCSR, APC_StateBatch
// L7 DeviceLayout  -> candidate-major X[B,n]
// L8 Operator ABI  -> apc_* launch wrappers
// L9 Ledger        -> kernel/copy/violation metrics owned by the caller

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
  APC_OK = 0,
  APC_ERR_INVALID_ARGUMENT = 1,
  APC_ERR_CUDA = 2
} APC_Status;

typedef enum {
  APC_SENSE_LE = 0,
  APC_SENSE_GE = 1,
  APC_SENSE_EQ = 2
} APC_RowSense;

typedef struct {
  int32_t n_rows;
  int32_t n_vars;
  int32_t nnz;
  const int32_t* row_ptr;
  const int32_t* col_idx;
  const double* coeff;
  const double* rhs;
  const int8_t* sense;
  const double* weight;
} APC_LinearCSR;

typedef struct {
  int32_t batch_size;
  int32_t n_vars;
  int32_t* x;  // candidate-major, shape [B, n]
} APC_StateBatch;

typedef struct {
  int32_t batch_size;
  int32_t n_rows;
  double* response;   // shape [B, m]
  double* violation;  // shape [B, m]
  double* penalty;    // shape [B]
} APC_ViolationBatch;

typedef struct {
  const APC_LinearCSR* linear;
  APC_StateBatch* states;
  APC_ViolationBatch* violations;
  double* objective;  // shape [B], optional for this small example
  double* energy;     // shape [B]
  void* stream;       // cudaStream_t, kept opaque for C ABI sketches
} APC_RuntimeCtx;

APC_Status apc_eval_linear_csr(APC_RuntimeCtx* ctx);
APC_Status apc_rectify_linear_violation(APC_RuntimeCtx* ctx);
APC_Status apc_reduce_weighted_penalty(APC_RuntimeCtx* ctx);
APC_Status apc_project_binary(APC_RuntimeCtx* ctx);

#ifdef __cplusplus
}
#endif

