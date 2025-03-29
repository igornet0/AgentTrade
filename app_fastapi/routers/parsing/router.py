import asyncio
from fastapi import (APIRouter, Request, Depends, 
                     UploadFile, File, Form, HTTPException)
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from typing import List
import json

from apps import HandlerParser
from app_fastapi.routers.parsing.schemas import ParseRequest

import logging

logger = logging.getLogger("app_fastapi.parsing.routers")

router = APIRouter(prefix="/parse", tags=["Parsing"])
templates = Jinja2Templates(directory="app_fastapi/templates")

@router.get("/")
async def parse_interface(request: Request):
    parsers = HandlerParser.get_available_parsers()
    
    return templates.TemplateResponse(
        "parsing/index.html",
        {"request": request, "parsers": parsers}
    )

@router.get("/params/{parser_type}")
async def get_parser_params(parser_type: str):

    params = HandlerParser.get_parser_params(parser_type)
    
    methods = [m for m in dir(HandlerParser._parsers[parser_type]) 
               if not m.startswith('_') and callable(getattr(HandlerParser._parsers[parser_type], m))]
    
    return {"params": params, "methods": methods}

@router.get("/info/{parser_type}")
async def get_parser_info(parser_type: str):
    return HandlerParser.get_parser_info(parser_type)

@router.post("/start")
async def start_parsing(
    parser_type: str = Form(...),
    method: str = Form(...),
    init_params: str = Form(...),  
    method_params: str = Form(...), 
    files: List[UploadFile] = File(...)
):
    handler = HandlerParser()

    # Проверка расширений файлов
    allowed_extensions = ['.csv', '.xlsx']
    for file in files:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимое расширение файла: {file_ext}. Разрешены: {', '.join(allowed_extensions)}"
            )
    
    # Десериализуем параметры
    init_params_dict = json.loads(init_params)
    method_params_dict = json.loads(method_params)
    
    # Сопоставляем файлы с параметрами
    files_dict = {file.filename: file for file in files}
    
    result = await handler.run_parser(
        parser_type=parser_type,
        method=method,
        init_params=init_params_dict,
        method_params=method_params_dict,
        files=files_dict
    )
    
    return {"status": "completed", "result": result.to_dict(orient='records')}

# @router.post("/start")
# async def start_parsing(request: ParseRequest):
#     handler = HandlerParser()
    
#     # Создаем экземпляр парсера
#     parser_instance = handler._parsers[request.parser_type](**request.init_params)
    
#     # Вызываем метод
#     method = getattr(parser_instance, request.method)
#     result = await method(**request.method_params)
    
#     return {"status": "completed", "result": result}

# @router.post("/start")
# async def start_parsing(request: ParseRequest):
#     handler = Handler()
#     result = await handler.run_parser(
#         parser_type=request.parser_type,
#         method=request.method,
#         params=request.params
#     )
#     return {"status": "completed", "result": result}