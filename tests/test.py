from transformers import pipeline
import pandas as pd
from urllib.parse import urlparse
import undetected_chromedriver as uc
from PIL import Image
from io import BytesIO

from App_web import NewsModel, DatasetTimeseries, NewsDataset

# dataset = pd.read_csv("datasets_news/crypto_news_api.csv",
#                                     parse_dates=["date"])
# print(dataset.head())

# df_t = dataset["title"]
# df_te = dataset["text"]
# df_d = dataset["date"]
# max_len = 0
# for title, text, date in zip(df_t, df_te, df_d):
#     if len(text) >= max_len:
#         max_len = len(text)
#         t = text
# print(t)

# domain = list(NewsDataset.get_domains(dataset))

# news_df = processor.analyze_sentiment(t)
# print(news_df)
# processor.get
options = uc.ChromeOptions() 
options.headless = True
driver = uc.Chrome(use_subprocess=True, options=options) 

def check_url(url):
    try:
        driver.get(f"http://{url}") 
        status_code = driver.execute_script("return document.readyState")
        driver.quit()
        if status_code == "complete":
            return True

    except Exception as e:
        return False

    return False

dataset = pd.read_csv("datasets_news/crypto_news_api.csv",
                                     parse_dates=["date"])
dataset2 = pd.read_csv("datasets_news/cryptonews.csv",
                                     parse_dates=["date"])
domain = NewsDataset.get_domains(dataset)
domain2 = NewsDataset.get_domains(dataset2)

print(len(domain), len(domain2))
# print(domain[:10], domain2[:10])

domains = []
domain_not_open = []

for url in domain:
    if not check_url(url):
        domain_not_open.append(url)
    else:
        domains.append(url)

for url in domain2:
    if not check_url(url):
        domain_not_open.append(url)
    else:
        domains.append(url)

df = pd.DataFrame({"domain": domains})
df.to_csv("datasets_news/domains.csv", index=False)
df = pd.DataFrame({"domain": domain_not_open})
df.to_csv("datasets_news/domains_not_open.csv", index=False)
