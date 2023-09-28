from src.interfaceadapters.repositories.stock_repo import StockRepo


def test_init():
    stock_repo = StockRepo()
    assert stock_repo is not None


def test_get_landing_stock_prices():
    stock_repo = StockRepo()
    df = stock_repo.get_landing_stock_prices()
    assert df is not None
    assert df.shape[0] > 0
    assert df.shape[1] > 0
    assert df.columns[0] == 'stock_indice'
    assert df.columns[1] == 'date'
    assert df.columns[2] == 'content'


def test_get_landing_news_sentiments():
    stock_repo = StockRepo()
    df = stock_repo.get_landing_news_sentiments()
    assert df is not None
    assert df.shape[0] > 0
    assert df.shape[1] > 0
    assert df.columns[0] == 'stock_indice'
    assert df.columns[1] == 'date'
    assert df.columns[2] == 'content'


def test_get_landing_social_sentiments():
    stock_repo = StockRepo()
    df = stock_repo.get_landing_social_sentiments()
    assert df is not None
    assert df.shape[0] > 0
    assert df.shape[1] > 0
    assert df.columns[0] == 'stock_indice'
    assert df.columns[1] == 'start_date'
    assert df.columns[2] == 'end_date'
    assert df.columns[3] == 'content'
