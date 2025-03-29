# import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

# # Проверка доступности MPS
# device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
# print(f"Using device: {device}")

# model_name = "deepseek-ai/deepseek-llm-67b-chat"  # Пример модели
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# # Убедимся, что pad_token_id установлен
# if tokenizer.pad_token_id is None:
#     tokenizer.pad_token_id = tokenizer.eos_token_id

# model = AutoModelForCausalLM.from_pretrained(
#     model_name, 
#     torch_dtype=torch.bfloat16, 
#     device_map="auto", 
#     offload_folder="./offload",
#     low_cpu_mem_usage=True
# )
# model.generation_config = GenerationConfig.from_pretrained(model_name)
# model.generation_config.pad_token_id = tokenizer.pad_token_id

# news = "Кандидат на пост губернатора Флориды Байрон Дональдс хочет добавить биток $BTC в портфель штата"
# time_elapsed = 5  # 5 минут

# messages=[
#     {"role": "system", "content": "You are a financial analyst assistant. Your task is to analyze cryptocurrency-related news and return a structured response in the form of a dictionary or table. For each coin mentioned or implied in the news, provide an impact factor (positive, negative, or neutral) based on the content of the news."},
#     {"role": "user", "content": f"""Can you analyze this news and write a list of coins it might affect, 
#              how exactly, and provide an impact coefficient of this news and in which direction (increase, decrease, or no impact)? 
#              If the news is not related to cryptocurrency, write only None; format everything in a table. News: {news}; Time elapsed: {time_elapsed}"""},
# ]

# # Применяем шаблон чата
# input_tensor = tokenizer.apply_chat_template(
#     messages, 
#     add_generation_prompt=True, 
#     return_tensors="pt"
# ).to(model.device)

# # Создаем attention_mask вручную
# attention_mask = torch.ones_like(input_tensor).to(model.device)

# # Генерация текста с использованием attention_mask
# outputs = model.generate(
#     input_tensor, 
#     attention_mask=attention_mask, 
#     max_new_tokens=100
# )

# result = tokenizer.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)
# print(result)

class NN_news:
    def __init__(self):
        pass