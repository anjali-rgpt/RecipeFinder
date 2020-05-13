from flask import Flask,request,render_template,session,redirect
import time
from bs4 import BeautifulSoup
from googlesearch import search
import urllib.request as urequest
import urllib.parse as parse

app=Flask(__name__)
app.secret_key='recipefinder'
#session['user']={}
relatedRecipeSearch=[]
sites=list()


headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'

@app.route('/')
def homepage():
    return render_template('configuration.html')

@app.route('/searchbyname', methods=["POST", "GET"])
def mainscraper():
    recipe=getrecipe()
    print(recipe)
    return render_template('displayrecipe.html',recipe_title=recipe['recipe_title'],rating=recipe['rating'],imageurl=recipe['imageurl'],ingredients=recipe['ingredients'],directions=recipe['directions'],relatedsites=recipe['relatedsites'],siteurl=recipe['siteurl'])


def getrecipe():
    if request.method=="POST":
        result=request.form
        keywords=result['keywords']
        siteurl=""
        for url in search(keywords+" allrecipes", tld='com', stop=1):
            page=urequest.urlopen(url)
            print(url)
            html_doc=BeautifulSoup(page,'html.parser')

            details=getdetails(html_doc)

            htmlIngredients = html_doc.findAll( 'span',{'class': "ingredients-item-name"})
            htmlDirections = html_doc.findAll('li',{'class': " subcontainer instructions-section-item"})
            y1=[]
            y2=[]
            flag=0
            if htmlIngredients==None or len(htmlIngredients)==0:
                s = html_doc.findAll( 'span',{'class': "recipe-ingred_txt added"})
                for element in s:
                    #print(element)
                    y1.append(element.string)
                

            if htmlDirections==None or len(htmlDirections)==0:
                s = html_doc.findAll( 'span',{'class': "recipe-directions__list--item"})
                print(s)
                for element in s:
                    print(element.string)
                    if element.string!=None:
                        y2.append(element.string)

            if len(y2)==0:
                s = html_doc.findAll( 'div',{'class': "section-body"})
                for element in s:
                    for x in element.contents:
                        if x.name=="p":
                            y2.append(x.string)
                flag=1

            ingredientList = []
            directionslist=[]

            if htmlIngredients==None or len(htmlIngredients)==0:
                ingredientList=y1
            else: 
                for ingredient in htmlIngredients:
                    if ingredient!=None:
                        ingredientList.append(ingredient.string)
            print(ingredientList)

            if htmlDirections==None or len(htmlDirections)==0 or flag==1:
                directionslist=y2
            else:
                for direction in htmlDirections:
                    if direction!=None:
                        directionslist.append(direction.string)
            print(directionslist)
            
            image1=html_doc.find('div', {'class':'recipe-content-container'})
            image2=html_doc.find('div', {'class':'summary-background'})

            if image1!=None:
                    
                for element in image1.descendants:
                    if element.name=="img":
                        imurl=element["src"]
                        break
            else:
                for element in image2.descendants:
                    if element.name=="img":
                        imurl=element["src"]
                        break

            siteurl=url
            print('Image URL:',imurl)
        time.sleep(10)
        sites=relatedsites()
        recipe={'recipe_title':details[0],'rating':details[1],'imageurl':imurl,'ingredients':ingredientList,'directions':directionslist,'relatedsites':sites,'siteurl':siteurl}
        
        r=recipe
        return r
        
def relatedsites():
    mainsites=[]
    if request.method=="POST":
        result=request.form
        keywords=result['keywords']
        print(keywords)
        for url in search(keywords+" recipe", tld='com', stop=20):
            site=parse.urlparse(url)[1]
            #print(site)
            if (len(mainsites)==0 or site not in mainsites) and 'allrecipes' not in site:
                mainsites.append(site)
                relatedRecipeSearch.append(url)
            mainsites=mainsites[:10]
            sites=relatedRecipeSearch[:10]
    return sites

def getdetails(doc):
    ratingstars=0
    try:
        stars=doc.find('span',{'class':'review-star-text'})
        if stars==None or len(stars)==0:
            stars=doc.find('div',{'class':'rating-stars'})
            ratingstars=round(float(stars["data-ratingstars"]),1)
            
        else:
            x=stars.string
            print(x)
            l=x.strip().split(" ")
            print(l)
            for i in l:
                try:
                    ratingstars=round(float(i),1)
                except:
                    pass
    except:
        ratingstars="Unrated by AllRecipes"

        
    print(ratingstars)        

    title=doc.find('h1').string
    print(title)
    return (title,ratingstars)



if __name__=='__main__':
    app.run(debug=True,port=8082)
