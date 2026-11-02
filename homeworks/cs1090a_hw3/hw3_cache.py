"""Supplied caching for expensive bootstrap results, without fitted-object pickles.

Checks cover the passed data, settings, function sources, dependencies, and package
versions. They cannot discover every external dependency of student code. Delete the
cache or use force=True after changing a model or its fitting implementation; also
update settings['implementation_version'] when changing that implementation.
"""

from pathlib import Path
import hashlib
import inspect
import json
import tempfile
import zipfile
import numpy as np
import pandas as pd
import sklearn


def _json_value(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Unsupported cache setting: {type(value).__name__}")


def _array_digest(value):
    a = np.asarray(value)
    if a.dtype.hasobject:
        raise TypeError(
            "Cache arrays must have numeric, boolean, or string dtypes, not object dtype."
        )
    h = hashlib.sha256()
    h.update(str(a.shape).encode())
    h.update(a.dtype.str.encode())
    h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def _data_digest(value):
    if isinstance(value, (pd.DataFrame, pd.Series)):
        h = hashlib.sha256()
        if isinstance(value, pd.DataFrame):
            h.update(repr(list(value.columns)).encode())
            h.update(repr(value.dtypes.astype(str).tolist()).encode())
        else:
            h.update(repr((value.name, str(value.dtype))).encode())
        h.update(pd.util.hash_pandas_object(value, index=True).to_numpy().tobytes())
        return h.hexdigest()
    return _array_digest(value)


def _source_digest(function):
    try:
        source = inspect.getsource(function)
    except (OSError, TypeError):
        raise ValueError(
            "Define the bootstrap function in a code cell or module so its source can be checked."
        ) from None
    return hashlib.sha256(source.encode()).hexdigest()


def cached_bootstrap_results(
    compute, *, cache_path, X, y, settings, dependencies=(), force=False
):
    """Return a mapping of array results, computing and saving it on a cache miss.

    compute() must return a dictionary of numeric, boolean, or string arrays.
    Pass all fitting settings (counts, grids, seeds, solver settings, preprocessing)
    and an explicit implementation_version. dependencies lists fitting functions or
    classes called by compute, whose source must also be checked. Plot code belongs
    after this call, so changing a figure does not invalidate the fitted results.
    """
    if not isinstance(settings.get("implementation_version"), str):
        raise ValueError(
            "Provide a string implementation_version in the cache settings."
        )
    path = Path(cache_path)
    recipe = {
        "schema": 1,
        "X": _data_digest(X),
        "y": _data_digest(y),
        "settings": settings,
        "compute_source": _source_digest(compute),
        "dependency_sources": [_source_digest(f) for f in dependencies],
        "versions": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    serialized = json.dumps(
        recipe, sort_keys=True, default=_json_value, allow_nan=False
    )
    fingerprint = hashlib.sha256(serialized.encode()).hexdigest()
    if path.exists() and not force:
        try:
            with np.load(path, allow_pickle=False) as saved:
                metadata = json.loads(str(saved["__metadata__"].item()))
                arrays = {
                    k: saved[k].copy() for k in saved.files if k != "__metadata__"
                }
            valid = metadata.get("fingerprint") == fingerprint and metadata.get(
                "array_digests"
            ) == {k: _array_digest(v) for k, v in arrays.items()}
            if valid:
                print("Loaded matching bootstrap results from cache.")
                return arrays
            print(
                "Cached inputs, settings, implementation, or results changed; recomputing."
            )
        except (OSError, ValueError, KeyError, zipfile.BadZipFile):
            print("The cache could not be validated; recomputing.")
    elif force:
        print("Forced fresh bootstrap computation.")
    arrays = compute()
    if not isinstance(arrays, dict) or not arrays or "__metadata__" in arrays:
        raise TypeError(
            "The bootstrap function must return a nonempty dictionary of array results."
        )
    arrays = {k: np.asarray(v) for k, v in arrays.items()}
    if any(not isinstance(k, str) for k in arrays):
        raise TypeError("Result names must be strings.")
    metadata = {
        "fingerprint": fingerprint,
        "array_digests": {k: _array_digest(v) for k, v in arrays.items()},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, suffix=".npz", delete=False
        ) as f:
            temp_path = Path(f.name)
            np.savez_compressed(
                f, __metadata__=np.asarray(json.dumps(metadata)), **arrays
            )
        temp_path.replace(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    print("Saved fresh bootstrap results to cache.")
    return arrays
