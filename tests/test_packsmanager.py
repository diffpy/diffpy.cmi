import pytest

from diffpy.cmi.packsmanager import PacksManager


@pytest.mark.parametrize(
    # 1) pack with no examples.  Expect {'empty_pack': []}
    # 2) pack with multiple examples.
    #  Expect {'full_pack': [('example1`, path_to_1'), 'example2', path_to_2)]
    # 3) multiple packs.  Expect dict with multiple pack:tuple pairs
    # 4) no pack found. Expect {}
    "input,expected",
    [
        # case 1: pack with no examples.  Expect {'empty_pack': []}
        (
            "case1",
            {"empty_pack": []},
        ),
        # case 2: pack with multiple examples.
        # Expect {'full_pack': [('example1', path_to_1),
        #           ('example2', path_to_2)]}
        (
            "case2",
            {
                "full_pack": [
                    ("example1", "path_to_1"),
                    ("example2", "path_to_2"),
                ]
            },
        )
        # case 3: multiple packs.  Expect dict with multiple pack:tuple pairs
        (
            "case3",
            {
                "pack1": [("ex1", "path1"), ("ex2", "path2")],
                "pack2": [("ex3", "path3")],
            },
        ),
        # (   # case 4: no pack found. Expect {}
        #     None,
        #     {},
        # )
    ],
)
def test_available_examples(input, expected, example_cases):
    test_path = (example_cases / input / "requirements" / "packs").resolve()
    # print("examples:", test_path)
    for path in test_path.rglob("*"):
        # print(" -", path.relative_to(example_cases))
        if path.suffix:
            assert path.is_file(), f"{path} should be a file"
        else:
            assert path.is_dir(), f"{path} should be a directory"
    pkmg = PacksManager(test_path)
    # print(pkmg.examples_dir)
    actual = pkmg.available_examples()
    assert actual == expected
