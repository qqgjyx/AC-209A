# Homework 3 environment and files

## Local setup with uv

Use the same environment workflow as in the earlier homework assignments. From the extracted assignment folder, run:

```bash
uv sync
uv run jupyter lab
```

The supplied project and lock files specify the environment. Keep these files together:

- The homework notebook.
- `hw3_support.py`, containing the supplied loading, preprocessing, and checkpoint helpers.
- `hw3_cache.py`, containing the bootstrap cache helper.
- The `data/` folder, containing `ames.csv`, `zoo.csv`, and `cookie_spectra.npz`.
- `pyproject.toml` and `uv.lock`.

The notebook reads the local data and does not download datasets. Package installation is the environment setup step and may require a connection. Do not move the notebook away from its helper and data files.

## Running the analyses

Run the setup cells before the questions. Use the supplied fixed partitions and folds. Each cross-validation fit must learn its preprocessing from that fold's fitting rows. The supplied reference pipeline is the checkpoint for later Ames work.

Bootstrap stability with penalty retuning performs many fits and takes longer than fitting one model. Record your results and reuse the bootstrap fits for the penalty-variability question. Do not rerun the entire analysis solely to redraw a plot.

Keep final test evaluation disabled until your modeling procedure and comparison set are frozen. Before submitting, restart the kernel and run the completed notebook from top to bottom. Include the required figures and written interpretations.

Use the replication counts in the notebook setup. After changing a model or its implementation, delete its cached results or force a refresh before using the outputs.

## Colab and other hosted environments

These environments must have the same required packages and all supplied local files, including the notebook file that Otter reads. Uploading only the CSV is insufficient. The revised draft has been checked in its supplied local environment; hosted-environment verification remains pending before release.
