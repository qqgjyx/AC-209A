"""Supplied HW3 setup/checkpoint helpers. No network access or hidden imputation code.

The category schema defines consistent coefficient identities from selection-predictor
metadata; learned replacement values and numeric scales are refitted on fitting rows.
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, lasso_path
from sklearn.model_selection import train_test_split, KFold, GroupKFold
from sklearn.pipeline import Pipeline

CORE = [
    "Gr_Liv_Area",
    "Total_Bsmt_SF",
    "First_Flr_SF",
    "Garage_Cars",
    "Garage_Area",
    "Year_Built",
    "Year_Remod_Add",
    "Full_Bath",
    "TotRms_AbvGrd",
    "Lot_Area",
    "Lot_Frontage",
    "Mas_Vnr_Area",
    "Year_Sold",
]


class FrontageImputer(BaseEstimator, TransformerMixin):
    """One transparent frontage rule; all fitted quantities come from fit(X)."""

    def __init__(self, method="neighborhood"):
        self.method = method

    def fit(self, X, y=None):
        """Learn replacement values from observed frontage in X only; y is unused."""
        z = X.copy()
        observed = z.Lot_Frontage.notna()
        self.median_ = float(z.loc[observed, "Lot_Frontage"].median())
        if not np.isfinite(self.median_):
            raise ValueError("No observed frontage in the fitting sample.")
        self.by_neighborhood_ = (
            z.loc[observed].groupby("Neighborhood").Lot_Frontage.median()
        )
        if self.method == "regression":
            self.regression_ = LinearRegression().fit(
                np.sqrt(z.loc[observed, ["Lot_Area"]]), z.loc[observed, "Lot_Frontage"]
            )
        elif self.method not in ("median", "neighborhood"):
            raise ValueError("Unknown frontage method.")
        return self

    def transform(self, X):
        """Return a copy with unknown frontage replaced using the previously fitted rule."""
        z = X.copy()
        missing = z.Lot_Frontage.isna()
        if self.method == "median":
            values = np.full(missing.sum(), self.median_)
        elif self.method == "neighborhood":
            values = (
                z.loc[missing, "Neighborhood"]
                .map(self.by_neighborhood_)
                .fillna(self.median_)
                .to_numpy()
            )
        else:
            values = (
                np.maximum(
                    1.0, self.regression_.predict(np.sqrt(z.loc[missing, ["Lot_Area"]]))
                )
                if missing.any()
                else []
            )
        z.loc[missing, "Lot_Frontage"] = values
        return z


class AmesPreprocessor(BaseEstimator, TransformerMixin):
    """Numeric scaling plus fixed-schema, unpooled 0/1 reference coding."""

    def __init__(
        self, numeric, categorical, categories, frontage_method="neighborhood"
    ):
        self.numeric = numeric
        self.categorical = categorical
        self.categories = categories
        self.frontage_method = frontage_method

    def fit(self, X, y=None):
        """Learn frontage replacements, numeric medians/scales, and encoding on X only."""
        self.frontage_ = FrontageImputer(self.frontage_method).fit(X)
        z = self.frontage_.transform(X)
        self.medians_ = z[self.numeric].median().fillna(0.0)
        self.scaler_ = StandardScaler().fit(z[self.numeric].fillna(self.medians_))
        self.encoder_ = OneHotEncoder(
            categories=self.categories,
            drop="first",
            handle_unknown="ignore",
            sparse_output=False,
        ).fit(z[self.categorical].fillna("Unknown"))
        self.feature_names_ = list(self.numeric) + list(
            self.encoder_.get_feature_names_out(self.categorical)
        )
        self.sources_ = list(self.numeric) + [
            c
            for c, levels in zip(self.categorical, self.categories)
            for _ in levels[1:]
        ]
        return self

    def transform(self, X):
        """Apply fitted preprocessing without relearning values from these houses."""
        z = self.frontage_.transform(X)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Found unknown categories")
            cats = self.encoder_.transform(z[self.categorical].fillna("Unknown"))
        return np.column_stack(
            [self.scaler_.transform(z[self.numeric].fillna(self.medians_)), cats]
        )

    def get_feature_names_out(self, input_features=None):
        """Return encoded names in the same column order as transform(X)."""
        return np.asarray(self.feature_names_, dtype=object)


def load_ames(path="data/ames.csv"):
    # Literal 'None' denotes absence in two amenity columns; it is not a blank.
    """Load raw records, predictor tables, fixed row-label splits, and a template.

    Mark unknown frontage as missing and preserve literal absence categories.
    Neighborhood-stratified splits use fixed seeds. Only selection predictors
    define the category schema; no outcome values determine preprocessing.
    The returned template remains unfitted until a fitting sample is supplied."""
    d = pd.read_csv(path, keep_default_na=False, na_values=[""])
    counts = d.Neighborhood.value_counts()
    strata = d.Neighborhood.where(
        d.Neighborhood.map(counts) >= 20, "Other_small_neighborhoods"
    )
    train, test = train_test_split(
        d.index.to_numpy(), test_size=0.25, random_state=109, stratify=strata
    )
    selection, inference = train_test_split(
        train, test_size=0.4, random_state=110, stratify=strata.loc[train]
    )
    # This supplied processed fixture contains basement-type codes under the
    # square-footage label. Omit that duplicated/mislabeled field, retaining
    # the actual basement-type factor and the other recorded basement areas.
    x = d.drop(columns=["Sale_Price", "BsmtFin_SF_1"]).copy()
    x.Lot_Frontage = x.Lot_Frontage.replace(0, np.nan)
    numeric = list(x.select_dtypes("number"))
    categorical = [c for c in x if c not in numeric]
    categories = [
        sorted(x.loc[selection, c].fillna("Unknown").unique()) for c in categorical
    ]
    template = AmesPreprocessor(numeric, categorical, categories)
    return (
        d,
        x,
        {"selection": selection, "inference": inference, "test": test},
        template,
    )


def reference_pipeline(template, estimator=None):
    """Build a cloned preprocessing-and-model pipeline for fold-specific fitting."""
    from sklearn.base import clone

    return Pipeline(
        [
            ("prep", clone(template)),
            ("model", LinearRegression() if estimator is None else estimator),
        ]
    )


def fixed_folds(n, seed=109, k=5):
    """Return reproducible (training, held-out) positional indices for n rows."""
    return list(KFold(k, shuffle=True, random_state=seed).split(np.arange(n)))


def bootstrap_folds(ids, seed, k=5):
    """Return folds that keep copies of the same original house together.

    ids gives the original house identifier for each resampled row. Grouping
    prevents one copy appearing in training while another is held out."""
    return list(
        GroupKFold(k, shuffle=True, random_state=seed).split(
            np.arange(len(ids)), groups=ids
        )
    )


def support_checkpoint(
    template, x_inference, candidate_indices, frequencies, min_support=10
):
    """Predictor-only support and rank checks; no inference outcomes accepted.

    Exclude a candidate when too few rows differ from its most common value,
    or when adding it does not increase the intercept-containing design rank.
    Exclusion means this design cannot support the planned coefficient inference;
    it does not establish that the predictor has no association with price.
    """
    from sklearn.base import clone

    prep = clone(template).fit(x_inference)
    a = prep.transform(x_inference)
    keep = []
    report = []
    design = np.ones((len(a), 1))
    rank = 1
    order = sorted(
        candidate_indices, key=lambda j: (-frequencies[j], prep.feature_names_[j])
    )
    for j in order:
        counts = np.unique(a[:, j], return_counts=True)[1]
        support = len(a) - counts.max()
        candidate = np.column_stack([design, a[:, j]])
        new_rank = np.linalg.matrix_rank(candidate)
        reason = "retained"
        if support < min_support:
            reason = "inadequate predictor support"
        elif new_rank <= rank:
            reason = "constant or linearly dependent in frozen design"
        else:
            keep.append(j)
            design = candidate
            rank = new_rank
        report.append(
            {
                "term": prep.feature_names_[j],
                "frequency": frequencies[j],
                "nonmodal_support": int(support),
                "decision": reason,
            }
        )
    if rank != len(keep) + 1:
        raise ValueError("Frozen design is not full-rank.")
    return np.asarray(keep, dtype=int), pd.DataFrame(report)


def checked_ols(template, x, y, keep, evaluation=None):
    """Fit OLS on the retained encoded columns and check coefficient identifiability.

    Learn preprocessing from x only. Return the fitted preprocessing, design,
    coefficients, residuals, and residual noise estimate. If evaluation rows
    are supplied, transform them without refitting and return predictions.
    A rank-deficient fitting design raises an error rather than reporting
    misleading coefficient uncertainty."""
    from sklearn.base import clone

    prep = clone(template).fit(x)
    a = np.column_stack([np.ones(len(x)), prep.transform(x)[:, keep]])
    if np.linalg.matrix_rank(a) != a.shape[1]:
        raise ValueError(
            "An OLS fitting sample lacks coefficient identifiability; inspect support/rank."
        )
    coef = np.linalg.lstsq(a, y, rcond=1e-10)[0]
    pred = a @ coef
    result = {
        "prep": prep,
        "design": a,
        "coef": coef,
        "residuals": np.asarray(y) - pred,
        "sigma": np.sqrt(np.sum((np.asarray(y) - pred) ** 2) / (len(x) - a.shape[1])),
    }
    if evaluation is not None:
        result["evaluation_design"] = np.column_stack(
            [np.ones(len(evaluation)), prep.transform(evaluation)[:, keep]]
        )
        result["prediction"] = result["evaluation_design"] @ coef
    return result


def load_cookie(path="data/cookie_spectra.npz"):
    """Load calibration spectra, sucrose percentages, and wavelength values; omit documented outlier 23."""
    d = np.load(path)
    # Source identifies calibration observation 23 as an outlier (one-based index).
    # Brown, Fearn & Vannucci (2001); CRAN fds Biscuit documentation.
    mask = np.arange(len(d["calibration_y"])) != 22
    return d["calibration_X"][mask], d["calibration_y"][mask], d["wavelengths"]


def load_cookie_test(path="data/cookie_spectra.npz"):
    """Call only at final evaluation, after choices are frozen."""
    d = np.load(path)
    return d["prediction_X"], d["prediction_y"]


def bootstrap_coefficient_maps(template, X, keep, reference_sd, bootstrap_indices):
    """Construct response-independent OLS maps for the supplied bootstrap rows.

    Replacement values and scales are relearned from each resample's predictors.
    Numeric effects are per one reference-sample SD; indicators stay 0/1.
    Multiplying each map by the original response gives that resample's
    coefficients. Reuse the same maps for every response permutation.
    """
    from sklearn.base import clone

    maps = []
    for idx in bootstrap_indices:
        prep = clone(template).fit(X.iloc[idx])
        design = np.column_stack(
            [np.ones(len(idx)), prep.transform(X.iloc[idx])[:, keep]]
        )
        if np.linalg.matrix_rank(design, tol=1e-10) != design.shape[1]:
            raise ValueError(
                "Unidentified coefficient in a bootstrap design; inspect support/rank before interpreting intervals."
            )
        mult = np.array(
            [
                (
                    reference_sd[j] / prep.scaler_.scale_[j]
                    if j < len(reference_sd)
                    else 1.0
                )
                for j in keep
            ]
        )
        pinv = np.linalg.pinv(design, rcond=1e-10)[1:] * mult[:, None]
        op = np.zeros((len(keep), len(X)))
        np.add.at(op.T, idx, pinv.T)
        maps.append(op)
    return np.asarray(maps)
