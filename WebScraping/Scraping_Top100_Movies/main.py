import requests 
from bs4 import BeautifulSoup


response = requests.get("https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/")


Web_Data = response.text
Soup = BeautifulSoup(Web_Data,"html.parser")


Films_Titles = [name.getText() for name in Soup.find_all(name="h3",class_="title")]


Films_Titles.reverse()


with open("movies.txt","w",encoding="utf-8") as file:
    for i in range(len(Films_Titles)):
        file.write(f"{Films_Titles[i]}\n")
        
