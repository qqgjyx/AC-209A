# HW2: Where to run this notebook

**Use the first option that works for you.**

## 1. Your own laptop, with uv (recommended)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these two
commands in the folder you unzipped this homework into:

```bash
uv sync              # creates .venv with the exact package versions this homework needs
uv run jupyter lab
```

`uv sync` reads `pyproject.toml` and `uv.lock`, which pin Python and every package
version. Because the versions are pinned, your environment matches the one the graders
use, and it will still match if you come back to the assignment next week.

## 2. Google Colab (backup)

Colab works, with one limitation you need to plan around.

- **`grader.check(...)` cells will error on Colab.** Those checks read the notebook file
  itself, which Colab does not expose. This is not a problem for your grade: skip them
  while you work, and you will get the same feedback from the Gradescope autograder as
  soon as you upload.
- Upload `data/ames.csv` alongside the notebook, in a `data/` folder, each time you start a
  session. Colab deletes uploaded files at the end of every session. The file is 1.4 MB and
  the notebook reads it with `pd.read_csv("data/ames.csv")`, so the folder name matters.

```python
!pip -q install otter-grader
```

## Whichever you use

The notebook needs no network access: everything it computes comes from `data/ames.csv`.
Before you upload, restart the kernel, run all cells, and confirm it completes without an
error and that every plot and printed result is visible.
