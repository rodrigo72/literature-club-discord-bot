import ply.yacc as yacc
from suggestion_lexer import tokens
from typing import Tuple


def p_All(p):
    r"""All : Suggestions
            | Text Suggestions
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_Suggestions(p):
    r"""Suggestions : Suggestions Suggestion
                    | Suggestion
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_Suggestion(p):
    r"""Suggestion : Title OtherElements
    """
    p[0] = [p[1]] + p[2]


def p_OtherElements(p):
    r"""OtherElements : OtherElements OtherElement
                      |
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1] + [p[2]]


def p_OtherElement(p):
    r"""OtherElement : Author
                     | Description
                     | Genre
                     | Date
                     | Notes
                     | Reviews
                     | Links
                     | Download
                     | Pages
                     | Goodreads
                     | Wikipedia
                     | Quotes
    """
    p[0] = p[1]


def p_Title(p):
    r"""Title : TITLE SEMICOLON Text"""
    p[0] = ('title', p[3])


def p_Author(p):
    r"""Author : AUTHOR SEMICOLON Text"""
    p[0] = ('author', p[3])


def p_Description(p):
    r"""Description : DESCRIPTION SEMICOLON Text"""
    p[0] = ('description', p[3])


def p_Genre(p):
    r"""Genre : GENRE SEMICOLON Text"""
    p[0] = ('genre', p[3])


def p_Date(p):
    r"""Date : DATE SEMICOLON Text"""
    p[0] = ('date', p[3])


def p_Notes(p):
    r"""Notes : NOTES SEMICOLON Text"""
    p[0] = ('notes', p[3])


def p_Reviews(p):
    r"""Reviews : REVIEWS SEMICOLON Text"""
    p[0] = ('reviews', p[3])


def p_Links(p):
    r"""Links : LINKS SEMICOLON Text"""
    p[0] = ('links', p[3])


def p_Download(p):
    r"""Download : DOWNLOAD SEMICOLON Text"""
    p[0] = ('downloads', p[3])


def p_Pages(p):
    r"""Pages : PAGES SEMICOLON Text"""
    p[0] = ('pages', p[3])


def p_Goodreads(p):
    r"""Goodreads : GOODREADS SEMICOLON Text"""
    p[0] = ('goodreads', p[3])


def p_Wikipedia(p):
    r"""Wikipedia : WIKIPEDIA SEMICOLON Text"""
    p[0] = ('wikipedia', p[3])


def p_Quotes(p):
    r"""Quotes : QUOTES SEMICOLON Text"""
    p[0] = ('quotes', p[3])


def p_Text(p):
    r"""Text : Text TEXT
             |
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1] + [p[2]]


def p_error(p):
    print("Syntax error in input!", p)
    parser.exito = False


def print_nested_array(array, level=0, tuple=False):
    indent = '  ' * level
    for item in array:
        if isinstance(item, list):
            print(f"{indent}[")
            print_nested_array(item, level + 1)
            print(f"{indent}]")
        elif tuple and isinstance(item, Tuple):
            print(f"{indent}(")
            print_nested_array(item, level + 1)
            print(f"{indent})")
        else:
            print(f"{indent}{item}")


def nested_array_to_string(array, level=0, tuple=False):
    indent = '  ' * level
    result = ''
    for item in array:
        if isinstance(item, list):
            result += f"{indent}[\n"
            result += nested_array_to_string(item, level + 1)
            result += f"{indent}]\n"
        elif tuple and isinstance(item, Tuple):
            result += f"{indent}("
            result += nested_array_to_string(item, level + 1)
            result += f"{indent})"
        else:
            result += f"{indent}{item}\n"
    return result


parser = yacc.yacc()
parser.exito = True


# Testing
if __name__ == '__main__':
    test = """
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

    test2 = """
    random text before suggestions
    
    título: hello hello
    _autor:_ asd asd asd
    nº páginas: 123
    descrição:
    > asdasd asd
    > asdasdasd asd
    
    título: hello again
    **autora**: asd asd
    """

    result = parser.parse(test2.lower())
    print_nested_array(result)
