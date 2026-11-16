# HW4: Where to run this notebook

**Use the first option that works for you.**

## 1. Your own laptop, with uv (recommended)

This is the same setup you used for Homework 0 to 3. Install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then, in the folder you
unzipped this homework into:

```bash
uv sync              # creates .venv with the exact package versions this homework needs
uv run jupyter lab
```

`uv sync` reads `pyproject.toml` and `uv.lock`, which pin Python 3.12 or 3.13 and every
package version. Two packages are new this time: `pymc`, which Parts 3 and 4 use to
sample from a posterior, and `arviz`, which summarizes the result. The first time a
notebook imports `pymc` it compiles part of itself, which can take twenty or thirty
seconds; that is normal and happens once per environment.

The data file, `data/college_admissions.csv`, ships in the bundle. Nothing in this
assignment reaches the network. Keep the notebook and the `data/` folder side by side,
because the setup cell reads `data/college_admissions.csv` by that relative path.

## 2. Google Colab (backup)

Colab works, with two limitations you need to plan around.

- **`grader.check(...)` cells will error on Colab.** Those checks read the notebook file
  itself, which Colab does not expose. This is not a problem for your grade: skip them
  while you work, and you will get the same feedback from the Gradescope autograder as
  soon as you upload. You still need the `otter` package for the first cell to run;
  Colab does not have it installed, so add a cell at the top with
  `!pip -q install otter-grader` (Colab has no `uv`; on your own laptop use `uv sync`).
- **Colab's PyMC may be a different version** from the one this assignment pins. The
  models in Parts 3 and 4 use only `pm.Normal`, `pm.HalfNormal`, `pm.Bernoulli`,
  `pm.Deterministic`, `pm.math.sigmoid` and `pm.sample`, which have not changed across
  recent versions, so the code runs; the posterior means may differ from the staff
  values in the third decimal, which is within the tests' tolerances.

Upload `data/college_admissions.csv` into a `data/` folder next to the notebook at the
start of every session, because Colab deletes your files when the session ends.

## Whichever you use

The notebook must run from top to bottom: restart the kernel, run all cells, and confirm
it completes without error before you upload. Every test in this assignment reads
variables defined in the setup cell (`train_df`, `test_df`, `y_train`, `y_test`,
`predictors`, `skf`), so run that cell first and do not change it. The four sampling
cells in Parts 3 and 4 take about fifteen seconds each; a full run of the notebook takes
two to three minutes.
