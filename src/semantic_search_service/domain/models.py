from typing import Any

from sentence_transformers import SentenceTransformer
from functools import lru_cache


model_name = "sentence-transformers/all-MiniLM-L6-v2"
asymmetric_model_name = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

mini_lm_model = SentenceTransformer(model_name)
asymmetric_model = SentenceTransformer(asymmetric_model_name)


class ModelNotFound(Exception):
    pass


@lru_cache
def get_model(model: str) -> Any:
    match model:
        case "mini_lm":
            return mini_lm_model
        case "mp_net":
            return asymmetric_model
    raise ModelNotFound(f"{model_name} not available")
