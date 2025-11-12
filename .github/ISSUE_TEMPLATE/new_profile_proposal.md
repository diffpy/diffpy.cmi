---
name: New Profile Proposal
about: Interested in contributing a new profile? Follow the instructions here!
title: "feat: add `<your-profile-name>` to `diffpy.cmi`"
labels: ""
assignees: ""
---

## Profile submission checklist

- [ ] Fork and clone this repository and cd to the top level by running `cd diffpy.cmi`.
- [ ] Create a requirements file by running `touch requirements/profiles/<your-profile-name>.yml`. List all packs used in this profile under the header `packs:` in a bulleted list. All additional packages used (if any) should be listed under `extras:` in a similar fashion (see [this file](https://github.com/diffpy/diffpy.cmi/blob/main/requirements/profiles/all.yml) for reference). If no additional packages are required, add the `extras:` header but leave the entries empty.
- [ ] List your profile and its dependencies under `docs/source/available-profiles.rst` using the same format as the other profiles. In this same file, add a description of your profile (1-2 sentences is recommended).

## Local testing

- [ ] Test to make sure the addition of your new profile worked by first creating a new environment and installing from source. Do this by running the following commands:

```
conda create -n testcmi-env diffpy.cmi
conda activate testcmi-env
pip install -e .
cmi install docs tests
```

- [ ] Run `cmi info` to see if your profile is listed there.
- [ ] Build and open the docs with the command `cd docs && make html && open build/html/index.html`. Navigate around the docs to make sure everything looks okay.
- [ ] Lastly, install your profile with `cmi install <your-profile-name>`.

When the above items are complete, make a pull request (PR) with the changes, referencing this issue in the PR (i.e. "closes #issue-number").
