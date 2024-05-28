from django import template

register = template.Library()


@register.inclusion_tag('include/markdown_to_html_tag.html', takes_context=True)
def markdown_to_html2(context, markdown_text: str) -> dict:
    # Делайте что-то с context, если нужно. В противном случае, его можно игнорировать в теле функции.
    # Пример возврата значения без использования context напрямую:
    return {'markdown_text': markdown_text.upper()}
