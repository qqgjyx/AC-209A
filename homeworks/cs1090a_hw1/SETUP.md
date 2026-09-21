# HW1: Where to run this notebook

**Use the first option that works for you.**

## 1. Your own laptop, with uv (recommended)

This is the same setup you used for Homework 0. Install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then, in the folder you
unzipped this homework into:

```bash
uv sync              # creates .venv with the exact package versions this homework needs
uv run jupyter lab
```

`uv sync` reads `pyproject.toml` and `uv.lock`, which pin Python 3.12 and every package
version. Because the versions are pinned, your environment matches the one the graders
use, and it will still match if you come back to the assignment next week.

## 2. Google Colab (backup)

Colab works, with two limitations you need to plan around.

- **`grader.check(...)` cells will error on Colab.** Those checks read the notebook file
  itself, which Colab does not expose. This is not a problem for your grade: skip them
  while you work, and you will get the same feedback from the Gradescope autograder as
  soon as you upload.
- **Colab deletes your files at the end of every session.** Your `data/` cache is deleted
  with them, so each new session would re-download everything, which is slow and puts
  avoidable load on the sites you are collecting from. Mount Google Drive and keep the
  notebook and `data/` there instead:

```python
from google.colab import drive
drive.mount('/content/drive')
%cd /content/drive/MyDrive/hw1     # keep the notebook + data/ here
!pip -q install otter-grader duckdb polars
```

## Whichever you use

Your submission must satisfy the Question 10 manifest, and the notebook must run
**offline** against the `data/` files you submit. That is exactly how it is graded, so it
is worth checking before you upload: restart the kernel, run all cells, and confirm it
completes without reaching the network.
