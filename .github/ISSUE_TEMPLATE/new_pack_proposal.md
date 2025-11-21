---
name: New Pack Proposal
about: Interested in contributing a new pack? Follow the instructions here!
title: "feat: add `<your-pack-name>` to `diffpy.cmi`"
labels: ""
assignees: ""
---

## Pack description

<pack description here>

## Pack submission checklist

- [ ] Fork and clone this repository and cd to the top level by running `cd diffpy.cmi`.
- [ ] Create a requirements file by running `touch requirements/packs/<your-pack-name>.txt`. List all dependencies for your pack.
- [ ] (OPTIONAL) Create a directory to place your examples, if applicable, by running `mkdir docs/examples/<your-pack-name>/<your-example-name>`.
- [ ] (OPTIONAL) Copy your example scripts and data under the directory you just made. If you have multiple examples, house them under their own separate directory (i.e. `.../<your-pack-name>/example1` and `.../<your-pack-name>/example2`).
- [ ] (OPTIONAL) Make a file under `docs/source/tutorial/` call `<your-pack-name>.rst` with `cp docs/source/tutorial/core.rst docs/source/tutorial/<your-pack-name>.rst`. Add your examples to the file in the same format as listed.
- [ ] List your pack and its dependencies under `docs/source/available-packs.rst` using the same format as the other packs. In this same file, add a description of your pack (1-2 sentences is recommended).
- [ ] Give yourself credit by listing your name and contributors to the pack you've created!

## Local testing

- [ ] Test to make sure the addition of your new pack worked by first creating a new environment and installing from source. Do this by running the following commands:

```
conda create -n testcmi-env diffpy.cmi
conda activate testcmi-env
pip install -e .
cmi install docs tests
```

- [ ] Run `cmi info` to see if your pack and any examples you may have added are listed there.
- [ ] Build and open the docs with the command `cd docs && make html && open build/html/index.html`. Navigate around the docs to make sure everything looks okay.
- [ ] Lastly, install your pack with `cmi install <your-pack-name>`.

When the above items are complete, make a pull request (PR) with the changes, referencing this issue in the PR (i.e. "closes #issue-number").
