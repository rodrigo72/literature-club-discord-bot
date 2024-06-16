import ply.lex as lex

tokens = (
    'SEMICOLON',
    'TEXT',
    'TITLE',
    'AUTHOR',
    'GENRE',
    'DESCRIPTION',
    'DATE',
    'NOTES',
    'REVIEWS',
    'LINKS',
    'PAGES',
    'DOWNLOAD',
    'GOODREADS',
    'WIKIPEDIA',
    'QUOTES'
)

t_ignore = ' \n\t'


def t_SEMICOLON(t):
    r'\:'
    t.value = t.value[0]
    return t


def t_TITLE(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>titles|title|título|títulos|titulos|titulo|nome|nomes)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_AUTHOR(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>autores|autoras|autora|authors|author|autor)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_GENRE(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>genres|géneros|generos|categorias|género|genero|genre)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_DESCRIPTION(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>description|descrição|descriçao|descricao|summary|sinopse|resumo)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_DATE(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>publication\sdate|data\sde\spublicação|data\sde\spublicaçao|data\sde\spublicacao|release\sdate|data|date)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_NOTES(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>comments|comment|comentários|comentarios|comentário|comentario|thoughts|footnotes|footnote|notes|notas|nota|note)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_REVIEWS(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>reviews|review|avaliações|avaliaçoes|avaliacoes|avaliação|avaliaçao|avaliacao)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_GOODREADS(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>goodreads|link do goodreads)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_WIKIPEDIA(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>wikipedia|wikipédia|link\sda\swikipédia|link\sda\swikipedia|link\sdo\swikipedia|link\sdo\swikipédia|wikipédia|wikipedia|wiki)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_LINKS(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>link.*(?=\:)|links|link)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_PAGES(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>número\sde\spáginas|numero\sde\spáginas|número\sde\spaginas|numero\sde\spaginas|nº\sde\spáginas|nº\sde\spaginas|nº\spáginas|nº\spaginas|páginas|paginas|number\sof\spages|nº\sof\spages|nº\spages|pages|length|comprimento)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_DOWNLOAD(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>download|downloads|tranferir)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_QUOTES(t):
    r'([_*\>\-\.\=]*\s*)?(?P<val>quote|quotes|citações|citaçoes|citacoes|citação|citaçao|citacao)([^\:]{0,5})(?=\:)'
    t.value = t.lexer.lexmatch.group('val')
    return t


def t_TEXT(t):
    r'[^\n]+'
    return t


def t_error(t):
    print(f"Illegal character: {t.value[0]}")
    raise lex.LexError("Illegal character")


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


lexer = lex.lex()


# Testing
def main():
    test_str = """
> Title: piranesi
> Author: Susanna Clarke
> Publication date: September 2020 
> Genre: Fantasy, Fiction

> Description: Piranesi’s house is no ordinary building: its rooms are infinite, its corridors endless, its walls are lined with thousands upon thousands of statues, each one different from all the others. Within the labyrinth of halls an ocean is imprisoned; waves thunder up staircases, rooms are flooded in an instant. But Piranesi is not afraid; he understands the tides as he understands the pattern of the labyrinth itself. He lives to explore the house.
> There is one other person in the house—a man called The Other, who visits Piranesi twice a week and asks for help with research into A Great and Secret Knowledge. But as Piranesi explores, evidence emerges of another person, and a terrible truth begins to unravel, revealing a world beyond the one Piranesi has always known.

> Wikipedia: https://en.wikipedia.org/wiki/Piranesi_(novel)
> Reviews: https://www.goodreads.com/book/show/50202953-piranesi
> Download: https://oceanofpdf.com/authors/susanna-clarke/pdf-epub-piranesi-download-85471341683/
"""

    lexer.input(test_str.lower())
    for token in lexer:
        print(f"Token(type='{token.type}', value='{token.value}')")


if __name__ == '__main__':
    main()
