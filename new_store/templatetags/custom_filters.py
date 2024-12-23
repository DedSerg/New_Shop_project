from django import template

register = template.Library()


@register.filter
def add_class_and_placeholder(field, css_class):
    """Добавляет CSS класс и placeholder к полю формы."""
    return field.as_widget(attrs={"class": css_class, "placeholder": field.label})


@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент и возвращает результат.

    Если происходит ошибка, возвращает пустую строку.
    """
    try:
        # Приведение к float для обработки чисел и строк
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''  # Возвращаем пустую строку в случае ошибки


@register.simple_tag
def my_custom_tag():
    """Возвращает строку 'Hello, World!'."""
    return "Hello, World!"
