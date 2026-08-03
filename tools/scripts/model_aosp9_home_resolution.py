#!/usr/bin/env python3
"""Small, auditable model of the Android 9 HOME chooser path.

This is deliberately not a general Android resolver implementation.  It models
only the fields and branches used by PackageManagerService.chooseBestActivity()
and findPreferredActivity() in the Android 9 sources kept in this repository.
It accepts JSON so a future device capture can be replayed without a device.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional


# IntentFilter.MATCH_CATEGORY_MASK.  The Fire decompiler prints the same value
# as decimal 268369920 in PackageManagerService.findPreferredActivity().
MATCH_CATEGORY_MASK = 0x0FFF0000


@dataclass(frozen=True)
class Candidate:
    component: str
    package: str
    priority: int
    preferred_order: int = 0
    is_default: bool = True
    match: int = 0x108000
    system: bool = False
    instant_app: bool = False

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Candidate":
        component = str(value["component"])
        package = str(value.get("package", component.split("/", 1)[0]))
        return cls(
            component=component,
            package=package,
            priority=int(value.get("priority", 0)),
            preferred_order=int(value.get("preferred_order", 0)),
            is_default=bool(value.get("is_default", True)),
        match=int(value.get("match", 0x108000), 0)
            if isinstance(value.get("match", 0x108000), str)
            else int(value.get("match", 0x108000)),
            system=bool(value.get("system", False)),
            instant_app=bool(value.get("instant_app", False)),
        )


@dataclass(frozen=True)
class PreferredRecord:
    component: str
    match: int
    always: bool = True
    set_components: tuple[str, ...] = ()
    persistent: bool = False

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PreferredRecord":
        raw_match = value.get("match", 0x108000)
        match = int(raw_match, 0) if isinstance(raw_match, str) else int(raw_match)
        return cls(
            component=str(value["component"]),
            match=match,
            always=bool(value.get("always", True)),
            set_components=tuple(str(item) for item in value.get("set_components", [])),
            persistent=bool(value.get("persistent", False)),
        )


@dataclass
class Decision:
    selected: Optional[str]
    branch: str
    sorted_candidates: list[str] = field(default_factory=list)
    best_priority: Optional[int] = None
    preferred_considered: bool = False
    preferred_accepted: bool = False
    persistent_considered: bool = False
    persistent_accepted: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sort_key(candidate: Candidate) -> tuple[Any, ...]:
    # AOSP mResolvePrioritySorter: descending priority, preferredOrder, isDefault,
    # match, system, then package name ascending.  The stable input order is the
    # final tie behavior for an otherwise identical package/component.
    return (
        -candidate.priority,
        -candidate.preferred_order,
        -int(candidate.is_default),
        -candidate.match,
        -int(candidate.system),
        candidate.package,
    )


def _lookup(candidates: Iterable[Candidate], component: str) -> Optional[Candidate]:
    return next((item for item in candidates if item.component == component), None)


def _record_matches_query(record: PreferredRecord, query: list[Candidate]) -> bool:
    target = _lookup(query, record.component)
    if target is None:
        return False
    if record.match != (max(item.match for item in query) & MATCH_CATEGORY_MASK):
        return False
    # PreferredComponent.sameSet(query): the saved component set is expected to
    # describe the result set.  A missing set is the last-chosen form and is not
    # accepted when chooseBestActivity asks for an always record.
    current = {item.component for item in query}
    saved = set(record.set_components)
    if record.always and saved:
        if current != saved and not saved.issuperset(current):
            return False
    elif record.always and not saved:
        return False
    return True


def choose_best_activity(
    candidates: Iterable[Candidate],
    ordinary_preferred: Optional[PreferredRecord] = None,
    persistent_preferred: Optional[PreferredRecord] = None,
) -> Decision:
    query = list(candidates)
    ordered = sorted(query, key=_sort_key)
    names = [item.component for item in ordered]
    if not ordered:
        return Decision(None, "empty-query", names, notes=["No HOME candidate survived query filtering."])
    if len(ordered) == 1:
        return Decision(ordered[0].component, "single-candidate", names, ordered[0].priority)

    top, second = ordered[0], ordered[1]
    decision = Decision(
        selected=None,
        branch="unresolved-resolver",
        sorted_candidates=names,
        best_priority=top.priority,
    )

    if (
        top.priority != second.priority
        or top.preferred_order != second.preferred_order
        or top.is_default != second.is_default
    ):
        decision.selected = top.component
        decision.branch = "top-ranking-fields-differ"
        decision.notes.append(
            "chooseBestActivity returns query[0] before ordinary preferred lookup."
        )
        return decision

    decision.persistent_considered = persistent_preferred is not None
    if persistent_preferred and _record_matches_query(persistent_preferred, ordered):
        decision.selected = persistent_preferred.component
        decision.branch = "persistent-preferred"
        decision.persistent_accepted = True
        return decision

    decision.preferred_considered = ordinary_preferred is not None
    if ordinary_preferred and ordinary_preferred.always and _record_matches_query(
        ordinary_preferred, ordered
    ):
        decision.selected = ordinary_preferred.component
        decision.branch = "ordinary-preferred"
        decision.preferred_accepted = True
        return decision

    decision.branch = "resolver-or-chooser"
    decision.notes.append(
        "No usable preferred record matched; Android 9 would continue to instant-app or resolver handling."
    )
    return decision


def fire_vs_priority_zero() -> Decision:
    fire = Candidate(
        component="com.amazon.firelauncher/.Launcher",
        package="com.amazon.firelauncher",
        priority=50,
        match=0x108000,
        system=True,
    )
    p0 = Candidate(
        component="org.fireosresearch.home.p0/org.fireosresearch.home.HomeActivity",
        package="org.fireosresearch.home.p0",
        priority=0,
        match=0x108000,
        system=False,
    )
    return choose_best_activity(
        [fire, p0],
        ordinary_preferred=PreferredRecord(
            component=p0.component,
            # PreferredComponent stores the category portion (0x100000 for
            # the captured HOME match 0x108000), not the complete ResolveInfo
            # match value.
            match=0x100000,
            always=True,
            set_components=(fire.component, p0.component),
        ),
    )


def _load_json(path: Path) -> Decision:
    data = json.loads(path.read_text(encoding="utf-8"))
    candidates = [Candidate.from_dict(item) for item in data.get("candidates", [])]
    ordinary = (
        PreferredRecord.from_dict(data["ordinary_preferred"])
        if data.get("ordinary_preferred")
        else None
    )
    persistent = (
        PreferredRecord.from_dict(data["persistent_preferred"])
        if data.get("persistent_preferred")
        else None
    )
    return choose_best_activity(candidates, ordinary, persistent)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scenario", choices=["fire-vs-p0"])
    group.add_argument("--input", type=Path, help="JSON replay input")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    decision = fire_vs_priority_zero() if args.scenario else _load_json(args.input)
    print(json.dumps(decision.to_dict(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
