import ghost

ghost.open('https://google.com')

width, resource = ghost.evaluate("document.getElementById('lga').offsetWidth;")

print(width)
