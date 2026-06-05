#pragma once

// Public CUDA operator ABI for the APC native runtime.
//
// The ABI is intentionally operator-based: each launch wrapper owns one tensor
// boundary and returns an APC_Status that host code can record or validate.

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
  int32_t* x;  // Candidate-major, shape [batch_size, n_vars].
} APC_StateBatch;

typedef struct {
  int32_t batch_size;
  int32_t n_rows;
  double* response;   // Shape [batch_size, n_rows], stores raw Ax values.
  double* violation;  // Shape [batch_size, n_rows], stores nonnegative values.
  double* penalty;    // Shape [batch_size].
} APC_ViolationBatch;

typedef struct {
  int32_t n_clauses;
  int32_t n_vars;
  int32_t nnz;
  const int32_t* clause_ptr;
  const int32_t* lit_var;
  const int8_t* lit_sign;
  const double* weight;
} APC_ClauseCSR;

typedef struct {
  int32_t batch_size;
  int32_t n_clauses;
  int32_t* unsatisfied;  // Shape [batch_size, n_clauses].
  double* penalty;       // Shape [batch_size], optional.
} APC_ClauseBatch;

typedef struct {
  int32_t n_vars;
  int32_t nnz;
  const int32_t* i;
  const int32_t* j;
  const double* q;
  const double* linear;
} APC_QUBOCOO;

typedef struct {
  const APC_LinearCSR* linear;
  APC_StateBatch* states;
  APC_ViolationBatch* violations;
  double* objective;  // Shape [batch_size], optional for this build skeleton.
  double* energy;     // Shape [batch_size], optional for this build skeleton.
  void* stream;       // cudaStream_t kept opaque for the C ABI.
} APC_RuntimeCtx;

APC_Status apc_eval_linear_csr(APC_RuntimeCtx* ctx);
APC_Status apc_rectify_linear_violation(APC_RuntimeCtx* ctx);
APC_Status apc_reduce_weighted_penalty(APC_RuntimeCtx* ctx);
APC_Status apc_project_binary(APC_RuntimeCtx* ctx);
APC_Status apc_eval_clause_csr(
    const APC_ClauseCSR* clauses,
    const APC_StateBatch* states,
    APC_ClauseBatch* output,
    void* stream);
APC_Status apc_eval_qubo_energy(
    const APC_QUBOCOO* qubo,
    const APC_StateBatch* states,
    double* energy,
    void* stream);

#ifdef __cplusplus
}
#endif
