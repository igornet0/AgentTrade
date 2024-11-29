from App_web import create_app, Dataset

def inint_pd():
    path_coins = "datasets_coins"
    path_news_urls = "datasets_news/domains.csv"

    dataset_coins = Dataset(path_coins, save=False)
    dataset_news_urls = Dataset(path_news_urls, save=False)

    return dataset_coins, dataset_news_urls

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)