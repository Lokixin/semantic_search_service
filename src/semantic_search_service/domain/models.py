from enum import StrEnum
from typing import Any

from sentence_transformers import SentenceTransformer
from functools import lru_cache


model_name = "sentence-transformers/all-MiniLM-L6-v2"
asymmetric_model_name = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

mini_lm_model = SentenceTransformer(model_name)
asymmetric_model = SentenceTransformer(asymmetric_model_name)


class ModelNotFound(Exception):
    pass

class Model(StrEnum):
    MINI_LM = "mini_lm"
    MP_NET = "mp_net"


@lru_cache
def get_model(model: Model) -> Any:
    match model:
        case Model.MINI_LM:
            return mini_lm_model
        case Model.MP_NET:
            return asymmetric_model
    raise ModelNotFound(f"{model_name} not available")
