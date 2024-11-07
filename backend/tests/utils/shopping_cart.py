from tests.utils.recipe import URL_GET_RECIPE, URL_RECIPES

# Адреса страниц
URL_SHOPPING_CART = URL_GET_RECIPE + 'shopping_cart/'
URL_DOWNLOAD_SHOPPING_CART = URL_RECIPES + 'download_shopping_cart/'

# Информация для валидации
TXT_CONTENT_TYPES = 'text/plain'
PDF_CONTENT_TYPES = 'application/pdf'
CSV_CONTENT_TYPES = 'text/csv'
ALLOWED_CONTENT_TYPES = (
    TXT_CONTENT_TYPES,
    PDF_CONTENT_TYPES,
    CSV_CONTENT_TYPES
)
