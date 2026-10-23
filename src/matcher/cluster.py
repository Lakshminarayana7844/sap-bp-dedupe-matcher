"""Union-find clustering of matched pairs into duplicate groups."""
from __future__ import annotations


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[int, int] = {}

    def find(self, x: int) -> int:
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def build_clusters(matched_pairs: list[tuple[int, int]]) -> list[list[int]]:
    """Cluster record indexes connected by matched pairs."""
    uf = UnionFind()
    for a, b in matched_pairs:
        uf.union(a, b)
    groups: dict[int, list[int]] = {}
    for a, b in matched_pairs:
        groups.setdefault(uf.find(a), set()).update((a, b))
    return sorted((sorted(v) for v in groups.values()), key=lambda g: g[0])
