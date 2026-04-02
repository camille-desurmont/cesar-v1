# Single source of truth for feature and target names used in training and in the contract. The
# design matrix column order (surface, pieces, dept, then one-hot type_local) must stay identical
# in train_and_export and in estimate_from_artifact; changing order here would break deployed models.
TARGET_NAME: str = "valeur_fonciere"

# Categories for type_local (order must be stable for one-hot encoding).
# Ideas: load from contract or config to add new types without code change.
TYPE_LOCAL_CATEGORIES: list[str] = [
    "Appartement",
    "Maison",
]

# Order of columns in the design matrix (after encoding). Used by train_and_export and contract.
MODEL_FEATURE_NAMES: list[str] = [
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "code_departement",
    *[f"type_local_{c}" for c in TYPE_LOCAL_CATEGORIES],
]
