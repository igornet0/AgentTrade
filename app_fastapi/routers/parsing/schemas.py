from pydantic import BaseModel
from typing import Dict, Any

class ParseRequest(BaseModel):
    parser_type: str
    method: str
    init_params: Dict[str, Any]
    method_params: Dict[str, Any]