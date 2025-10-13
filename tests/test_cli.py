import pytest

from diffpy.cmi import cli
from diffpy.cmi.packsmanager import PacksManager


def safe_get_examples(nonempty_packs, pack, n=None):
    """Return up to n examples if available."""
    exs = nonempty_packs.get(pack, [])
    if not exs:
        return []
    return exs if n is None else exs[:n]


def select_examples_subset(examples_dict, copy_type):
    """Select subset of examples depending on scenario.

    Handles edge cases where some packs may be empty.
    """
    subset = {}
    if not examples_dict:
        return {}
    nonempty_packs = {k: v for k, v in examples_dict.items() if v}
    if not nonempty_packs:
        return {}
    packs = list(nonempty_packs.keys())
    if copy_type == "one_example":
        pack = packs[0]
        exs = safe_get_examples(nonempty_packs, pack, 1)
        if exs:
            subset[pack] = exs
    elif copy_type == "multiple_examples_same_pack":
        pack = packs[0]
        exs = safe_get_examples(nonempty_packs, pack, 2)
        if exs:
            subset[pack] = exs
    elif copy_type == "multiple_examples_diff_packs":
        for pack in packs[:2]:
            exs = safe_get_examples(nonempty_packs, pack, 1)
            if exs:
                subset[pack] = exs
    elif copy_type == "pack_all_examples":
        pack = packs[0]
        exs = safe_get_examples(nonempty_packs, pack)
        if exs:
            subset[pack] = exs
    elif copy_type == "multi_packs_all_examples":
        for pack in packs[:2]:
            exs = safe_get_examples(nonempty_packs, pack)
            if exs:
                subset[pack] = exs
    elif copy_type == "combo_packs_and_examples":
        first_pack = packs[0]
        exs_first = safe_get_examples(nonempty_packs, first_pack, 1)
        if exs_first:
            subset[first_pack] = exs_first
        if len(packs) > 1:
            second_pack = packs[1]
            exs_second = safe_get_examples(nonempty_packs, second_pack)
            if exs_second:
                subset[second_pack] = exs_second
    elif copy_type == "all_packs_all_examples":
        subset = nonempty_packs
    else:
        raise ValueError(f"Unknown copy_type: {copy_type}")
    return subset


def verify_copied_files(subset, target_dir, case_dir):
    """Verify that all example files were copied correctly."""
    if not subset:
        if target_dir:
            assert not any(target_dir.iterdir())
        else:
            pass
        return
    dest = target_dir or case_dir
    assert dest.exists()
    for pack, examples in subset.items():
        for example_name, example_path in examples:
            for ex_file in example_path.rglob("*.py"):
                rel = ex_file.relative_to(example_path.parent.parent)
                dest_file = dest / rel
                assert dest_file.exists(), f"{dest_file} missing"


# Test copy_examples for various structural cases and copy scenarios.
# In total, 5 structural cases x 14 copy scenarios = 70 tests.
# The copy scenarios are:
# 1a) copy one example to cwd
# 1b) copy one example to a target dir
# 2a) copy multiple examples from same pack to cwd
# 2b) copy multiple examples from same pack to a target dir
# 3a) copy multiple examples from different packs to cwd
# 3b) copy multiple examples from different packs to a target dir
# 4a) copy all examples from a pack to cwd
# 4b) copy all examples from a pack to a target dir
# 5a) copy all examples from multiple packs to cwd
# 5b) copy all examples from multiple packs to target dir
# 6a) copy a combination of packs and examples to cwd
# 6b) copy a combination of packs and examples to target
# 7a) copy all examples from all packs to cwd
# 7b) copy all examples from all packs to a target dir

copy_scenarios = [
    ("one_example", "cwd"),
    ("one_example", "target"),
    ("multiple_examples_same_pack", "cwd"),
    ("multiple_examples_same_pack", "target"),
    ("multiple_examples_diff_packs", "cwd"),
    ("multiple_examples_diff_packs", "target"),
    ("pack_all_examples", "cwd"),
    ("pack_all_examples", "target"),
    ("multi_packs_all_examples", "cwd"),
    ("multi_packs_all_examples", "target"),
    ("combo_packs_and_examples", "cwd"),
    ("combo_packs_and_examples", "target"),
    ("all_packs_all_examples", "cwd"),
    ("all_packs_all_examples", "target"),
]


@pytest.mark.parametrize(
    "case_name",
    ["case1", "case2", "case3", "case4", "case5"],
)
@pytest.mark.parametrize(
    "copy_type, target_type",
    copy_scenarios,
)
def test_copy_examples(
    case_name, copy_type, target_type, example_cases, tmp_path
):
    """Test copy_examples for all structural and copy scenarios."""
    case_dir = example_cases / case_name
    pm = PacksManager(root_path=case_dir)
    examples_dict = pm.available_examples()
    target_dir = None if target_type == "cwd" else tmp_path / "target"
    if target_dir:
        target_dir.mkdir(parents=True, exist_ok=True)
    subset = select_examples_subset(examples_dict, copy_type)
    cli.copy_examples(subset, target_dir=target_dir)
    verify_copied_files(subset, target_dir, case_dir)
