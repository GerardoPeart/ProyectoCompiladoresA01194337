
import Prueba

while True:
    text = input('Hola > ')
    result = Prueba.Lexer.run(text)

    print(result)