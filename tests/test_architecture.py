"""Module boundaries (module-design.md M01, M02): imports and record ownership."""

import ast
from graphlib import CycleError, TopologicalSorter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent / "muninn"

# module-design.md "Dependency direction"
ALLOWED = {
    "web": {"workflows"},
    "workflows": {"content", "evidence", "practice", "measurement", "library"},
    "content": {"library"},
    "evidence": {"content", "library"},
    "practice": {"content", "evidence", "library"},
    "measurement": {"content", "evidence", "practice", "library"},
    "library": set(),
}
OWNERS = {"content", "evidence", "practice", "measurement", "workflows"}


def imported_modules(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "muninn":
                yield from (alias.name for alias in node.names)
            elif node.module.startswith("muninn."):
                yield node.module.split(".")[1]
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("muninn."):
                    yield alias.name.split(".")[1]


def violations(sources):
    """Return every forbidden import and foreign record access in ``sources``."""
    found = []
    for module, source in sources.items():
        tree = ast.parse(source)
        found += [
            f"{module} imports {other}"
            for other in sorted(set(imported_modules(tree)))
            if other != module and other not in ALLOWED[module]
        ]
        if module == "web":
            found += [
                f"web reaches into the store via .{node.attr}"
                for node in ast.walk(tree)
                if isinstance(node, ast.Attribute) and node.attr in {"store", "_conn"}
            ]
        for node in ast.walk(tree):
            for kw in getattr(node, "keywords", []):
                if kw.arg != "by":
                    continue
                if module == "library" and isinstance(kw.value, ast.Name) and kw.value.id == "by":
                    continue  # the Library forwards its caller's declared owner
                own = isinstance(kw.value, ast.Name) and kw.value.id == "OWNER"
                literal = isinstance(kw.value, ast.Constant) and kw.value.value == module
                if module not in OWNERS or not (own or literal):
                    found.append(f"{module} accesses records as {ast.unparse(kw.value)}")
    return found


def real_sources():
    return {p.stem: p.read_text() for p in PACKAGE.glob("*.py") if p.stem in ALLOWED}


def test_every_module_is_classified():
    assert {p.stem for p in PACKAGE.glob("*.py")} - {"__init__", "__main__"} <= set(ALLOWED)


def test_the_allowed_import_graph_is_acyclic():
    try:
        tuple(TopologicalSorter(ALLOWED).static_order())
    except CycleError as e:  # pragma: no cover - the assertion message is the point
        raise AssertionError(e) from e


def test_modules_import_and_write_only_what_they_own():
    assert violations(real_sources()) == []


def test_the_check_catches_seeded_violations():
    sources = real_sources()
    sources["content"] += "\nfrom muninn import evidence\n"
    sources["practice"] += "\nimport muninn.measurement\n"
    sources["evidence"] += "\ndef sneak(tx):\n    tx.put('schedule', {}, by='practice')\n"
    sources["measurement"] += "\ndef sneak(tx, who):\n    tx.current('attempt', by=who)\n"
    sources["web"] += "\ndef sneak(core):\n    return core.store.read(print)\n"
    found = violations(sources)
    assert "content imports evidence" in found
    assert "practice imports measurement" in found
    assert "evidence accesses records as 'practice'" in found
    assert "measurement accesses records as who" in found
    assert "web reaches into the store via .store" in found


def test_the_fsrs_adapter_is_private_to_practice():
    # module-design.md: the browser, Evidence and Measurement never touch engine state
    def imports_fsrs(node):
        if isinstance(node, ast.Import):
            return any(a.name.split(".")[0] == "fsrs" for a in node.names)
        return isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "fsrs"

    importers = {
        p.stem
        for p in PACKAGE.glob("*.py")
        for node in ast.walk(ast.parse(p.read_text()))
        if imports_fsrs(node)
    }
    assert importers == {"practice"}
    static = (PACKAGE / "static" / "app.js").read_text()
    assert "engine_state" not in static
