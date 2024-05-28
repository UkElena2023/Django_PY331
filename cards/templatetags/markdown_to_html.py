import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(name='markdown_to_html')
def markdown_to_html(markdown_text: str) -> str:
    """
    Преобразовывает текст из формата Markdown в HTML
    :param markdown_text: текст в формате Markdown
    :return: текст в формате HTML
    """
    # включение расширений для улучшенной работы обработки
    md_extensions = ['extra', 'fenced_code', 'tables']
    # преобразование из формата Markdown в HTML с расширениями
    html_content = markdown.markdown(markdown_text, extensions=md_extensions)

    return mark_safe(html_content)