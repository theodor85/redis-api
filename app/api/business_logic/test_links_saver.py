import pytest

from .links_saver import exctract_domains, remove_duplicates


def test_extract_domains():
    links = [
        "https://ya.ru",
        "https://ya.ru?q=123",
        "funbox.ru",
        "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor", 
    ]

    exctract_domains(links)

    assert links[0] == "ya.ru"
    assert links[1] == "ya.ru"
    assert links[2] == "funbox.ru"
    assert links[3] == "stackoverflow.com"


def test_remove_duplicates():
    links = [
        "https://ya.ru",
        "https://ya.ru?q=123",
        "funbox.ru",
        "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor", 
    ]

    exctract_domains(links)
    remove_duplicates(links)

    assert links[0] == "ya.ru"
    assert links[2] == "funbox.ru"
    assert links[3] == "stackoverflow.com"