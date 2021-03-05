from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 

import requests
import numpy as np

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

all_film = soup.find_all('div', attrs={'class':'lister-item mode-advanced'})
temp = [] #initiating a tuple

for film in all_film:
    #scrapping process
    title = film.find_all('a')[1].text.strip()
    
    imdb_rating = film.find_all('strong')[0].text.strip()
    
    extract_metascore = film.find_all('span', attrs={'class':'metascore favorable'})
    if not extract_metascore:
        metascore = np.nan
    else:
        metascore = extract_metascore[0].text.strip()
        
    votes = film.find_all('span', attrs={'name':'nv'})[0].text.strip()
    
    temp.append((title, imdb_rating, metascore, votes))

#change into dataframe
df = pd.DataFrame(temp, columns = ('title', 'imdb_rating', 'metascore', 'votes'))

#insert data wrangling here
df[['imdb_rating','metascore']] = df[['imdb_rating','metascore']].astype('float64')

df['votes'] = df['votes'].str.replace(",", "")
df['votes'] = df['votes'].astype('int64')

df['metascore'].fillna(df['metascore'].mean(), inplace = True)

df['metascore'] = df['metascore'].astype('int64')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'Rating {df["imdb_rating"].mean().round(2)}'

	top7_popular_film = df[['title', 'votes']].sort_values(by='votes', ascending=False).head(7)

	# generate plot
	ax = top7_popular_film.sort_values(by='votes', ascending=True).plot.barh(x='title', y='votes', figsize = (25,9))
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	votes_result = str(figdata_png)[2:-1]

	top7_highestrating_film = df[['title', 'imdb_rating']].sort_values(by='imdb_rating', ascending=False).head(7)
	ax_2 = top7_highestrating_film.sort_values(by='imdb_rating', ascending=True).plot.barh(x='title', y='imdb_rating', figsize = (25,9))

	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	rating_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		votes_result= votes_result,
		rating_result = rating_result
		)


if __name__ == "__main__": 
    app.run(debug=True)
