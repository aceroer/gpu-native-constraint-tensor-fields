"""Branch tensor objects for candidate repair routes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ctir import CTIRProblem
from .operators_cpu import Move, generate_moves
from .state_pool import StatePool


@dataclass(frozen=True)
class BranchRoute:
    """One candidate route inside a branch tensor."""

    state_index: int
    route_index: int
    move_type: str
    payload: tuple[int, ...]
    canonical_key: tuple[str, tuple[int, ...]]


@dataclass(frozen=True)
class BranchTensor:
    """Fixed-shape branch routes with an alive mask."""

    routes: tuple[tuple[BranchRoute, ...], ...]
    alive_mask: tuple[tuple[bool, ...], ...]
    metadata: tuple[tuple[dict[str, Any], ...], ...]

    def __post_init__(self) -> None:
        if len(self.routes) == 0:
            raise ValueError("BranchTensor.routes must not be empty")
        if len(self.alive_mask) != len(self.routes):
            raise ValueError("BranchTensor.alive_mask outer length must equal routes")
        if len(self.metadata) != len(self.routes):
            raise ValueError("BranchTensor.metadata outer length must equal routes")
        moves_per_state = len(self.routes[0])
        if moves_per_state == 0:
            raise ValueError("BranchTensor must include at least one route per state")
        for state_index, state_routes in enumerate(self.routes):
            if len(state_routes) != moves_per_state:
                raise ValueError("BranchTensor route rows must have fixed width")
            if len(self.alive_mask[state_index]) != moves_per_state:
                raise ValueError("BranchTensor alive mask rows must match route width")
            if len(self.metadata[state_index]) != moves_per_state:
                raise ValueError("BranchTensor metadata rows must match route width")
            for route_index, route in enumerate(state_routes):
                if route.state_index != state_index:
                    raise ValueError("BranchRoute.state_index must match tensor row")
                if route.route_index != route_index:
                    raise ValueError("BranchRoute.route_index must match tensor column")

    @property
    def batch_size(self) -> int:
        return len(self.routes)

    @property
    def routes_per_state(self) -> int:
        return len(self.routes[0])

    @property
    def shape(self) -> tuple[int, int]:
        return (self.batch_size, self.routes_per_state)

    @property
    def alive_count(self) -> int:
        return sum(1 for row in self.alive_mask for alive in row if alive)


def branch_tensor_from_state_pool(problem: CTIRProblem, pool: StatePool) -> BranchTensor:
    """Generate bit-flip branch routes from a StatePool."""

    move_rows = generate_moves(problem, pool.states)
    routes: list[tuple[BranchRoute, ...]] = []
    metadata: list[tuple[dict[str, Any], ...]] = []
    for state_index, row in enumerate(move_rows):
        route_row: list[BranchRoute] = []
        meta_row: list[dict[str, Any]] = []
        for route_index, move in enumerate(row):
            route = branch_route_from_move(move, route_index=route_index)
            route_row.append(route)
            meta_row.append({"origin": "generate_moves", "state_alive": pool.alive_mask[state_index]})
        routes.append(tuple(route_row))
        metadata.append(tuple(meta_row))
    alive_mask = tuple(
        tuple(pool.alive_mask[state_index] for _ in row)
        for state_index, row in enumerate(routes)
    )
    return BranchTensor(routes=tuple(routes), alive_mask=alive_mask, metadata=tuple(metadata))


def branch_route_from_move(move: Move, *, route_index: int) -> BranchRoute:
    """Convert a CPU bit-flip Move into a branch route."""

    payload = (move.var_index,)
    return BranchRoute(
        state_index=move.state_index,
        route_index=route_index,
        move_type="bit_flip",
        payload=payload,
        canonical_key=("bit_flip", payload),
    )


def canonical_branch_keys(tensor: BranchTensor) -> tuple[tuple[tuple[str, tuple[int, ...]], ...], ...]:
    """Return canonical branch keys without changing tensor shape."""

    return tuple(tuple(route.canonical_key for route in row) for row in tensor.routes)


def mask_branch_tensor(tensor: BranchTensor, alive_mask: tuple[tuple[bool, ...], ...]) -> BranchTensor:
    """Return a BranchTensor with an updated alive mask."""

    return BranchTensor(routes=tensor.routes, alive_mask=alive_mask, metadata=tensor.metadata)


def branch_tensor_summary(tensor: BranchTensor) -> dict[str, Any]:
    """Return a compact JSON-ready branch tensor summary."""

    return {
        "shape": list(tensor.shape),
        "alive_count": tensor.alive_count,
        "routes": [
            [
                {
                    "state_index": route.state_index,
                    "route_index": route.route_index,
                    "move_type": route.move_type,
                    "payload": list(route.payload),
                    "canonical_key": [route.canonical_key[0], list(route.canonical_key[1])],
                    "alive": tensor.alive_mask[state_index][route_index],
                }
                for route_index, route in enumerate(row)
            ]
            for state_index, row in enumerate(tensor.routes)
        ],
    }
