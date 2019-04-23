import urllib.request
from bs4 import BeautifulSoup

page = urllib.request.urlopen('http://www.google.com/')
soup = BeautifulSoup(page)

print(soup.prettify())


x = soup.body.find('div', attrs={'class' : 'container'}).text

#print(x)
