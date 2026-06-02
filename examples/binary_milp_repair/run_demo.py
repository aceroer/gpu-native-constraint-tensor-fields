from apc_example import BinaryDomain, LinearCSR, RepairConfig, StateBatch
from apc_example.repair_loop import repair_binary_milp


def main() -> None:
    domain = BinaryDomain(n_vars=3)
    linear = LinearCSR(
        n_rows=3,
        n_vars=3,
        row_ptr=(0, 2, 4, 6),
        col_idx=(0, 1, 1, 2, 0, 2),
        coeff=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
        rhs=(1.0, 1.0, 1.0),
        sense=(">=", ">=", "<="),
        weight=(1.0, 1.0, 1.0),
    )
    cost = (2.0, 1.0, 2.0)
    initial_batch = StateBatch(((0, 0, 0), (1, 1, 1), (1, 0, 0), (0, 1, 0)))

    result = repair_binary_milp(
        domain,
        linear,
        cost,
        initial_batch,
        RepairConfig(max_iters=8, lambda_penalty=10.0),
    )

    print("best_state:", result.best_state)
    print("best_objective:", result.best_objective)
    print("best_penalty:", result.best_penalty)
    print("ledger:")
    for row in result.ledger:
        print(" ", row)


if __name__ == "__main__":
    main()

