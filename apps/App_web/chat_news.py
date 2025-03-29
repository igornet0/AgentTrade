# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, BitsAndBytesConfig
from typing import Optional

app = FastAPI()

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализация модели при старте приложения
@app.on_event("startup")
async def load_model():
    global model, tokenizer, device

    # Квантование модели
    # quantization_config = BitsAndBytesConfig(
    #     load_in_8bit=True,  # 8-битное квантование
    # )
        
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")

    model_name = "deepseek-ai/deepseek-llm-67b-chat"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        offload_folder="./offload",
        low_cpu_mem_usage=True,
        # quantization_config=quantization_config  # Включаем квантование
    )
    model.generation_config = GenerationConfig.from_pretrained(model_name)
    model.generation_config.pad_token_id = tokenizer.pad_token_id

# Главная страница с формой
# main.py (измененная часть)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("chatNews.html", {"request": request})


# Обработка формы
@app.post("/analyze", response_class=HTMLResponse)
async def analyze_news(request: Request, news_text: str = Form(...)):
    print(f"news_text: {news_text}")
    try:
        messages=[
            {
                "role": "system", 
                "content": "You are a financial analyst assistant. Analyze cryptocurrency-related news and return a structured response in a table."
            },
            {
                "role": "user", 
                "content": f"""News: {news_text}; You can analyze the news and give it an assessment of the importance of the news from -100 to 100 for coins that this news can affect, where -100 is the maximum negative, 0 is neutral, 100 is the maximum positive; design it in the form of a table"""
            },
        ]

        input_tensor = tokenizer.apply_chat_template(
            messages, 
            add_generation_prompt=True, 
            return_tensors="pt"
        ).to(model.device)
        print(type(input_tensor))
        print()
        attention_mask = torch.ones_like(input_tensor).to(model.device)
        print(type(attention_mask))
        print()
        outputs = model.generate(
            input_tensor,
            attention_mask=attention_mask,
            max_new_tokens=60
        )
        print(outputs)
        print()
        result = tokenizer.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)
        print(result)
        
        # return templates.TemplateResponse("result.html", {
        #     "request": request,
        #     "news_text": news_text,
        #     "analysis_result": result
        # })
        
        return HTMLResponse(result)
    
    except Exception as e:
        return HTMLResponse(f"❌ Error: {str(e)}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)