# HW5: Where to run this notebook

**Use the first option that works for you.**

## 1. Your own laptop, with uv (recommended)

This is the same setup as the earlier homeworks. Install
[uv](https://docs.astral.sh/uv/getting-started/installation/), then, in the folder you
unzipped this homework into:

```bash
uv sync              # creates .venv with the exact package versions this homework needs
uv run jupyter lab
```

`uv sync` reads `pyproject.toml` and `uv.lock`, which pin Python 3.12 or 3.13 and every
package version. This homework needs no packages beyond those.

The data files ship in the bundle, in `data/`. Nothing in this assignment reaches the
network. Keep the notebook and the `data/` folder side by side, because the setup cell
reads the files by relative paths such as `data/X_train.csv`.

## 2. Google Colab is not supported for this homework

The Gradescope autograder re-runs your notebook with the package versions in `uv.lock` and
compares the submission files it writes with the ones you upload. Colab installs different
versions, and a different version can change a few predictions, so the files may not match and
your Kaggle questions would wait for a manual check. If you cannot run the notebook on your own
laptop, post on Ed and the staff will help you set it up.

## Whichever you use

The notebook must run from top to bottom in under 35 minutes: restart the kernel, run all
cells, and confirm it completes without error before you upload. The last cell prints the
runtime. The staff solution runs in about four minutes on a laptop.
