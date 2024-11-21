import requests 
from bs4 import BeautifulSoup

# Scraping Data from Hacker news website 

response = requests.get("https://news.ycombinator.com/news")

w = response.text

soup = BeautifulSoup(w,"html.parser")

links = []
texts = []
upvotes = []


# For Titles and Links
whole_title = soup.find_all("span",class_="titleline")
for title in whole_title:
    text = title.find("a")
    texts.append(text.getText())
    link = text.get("href")
    links.append(link)

    
# For Upvotes  
upvotes = [int(score.getText().split()[0]) for score in soup.find_all(name="span",class_="score")]

max_upvotes = max(upvotes)
max_pos = upvotes.index(max_upvotes) 
        
print(f"{texts[max_pos]}\n{links[max_pos]}\n{upvotes[max_pos]}\n#################")
    
    