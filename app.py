from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")


# Route to render index.html template using data from Mongo
@app.route("/")
def home():

    
        # Find one record of data from the mongo database
        fetchedMars_data = mongo.db.marscollection.find_one()

        if fetchedMars_data:
            title = fetchedMars_data["title"]
            news_paragraph = fetchedMars_data["news_paragraph"]
            featured_image_url= fetchedMars_data["featured_image_url"]
            mars_weather = fetchedMars_data["mars_weather"]
            marsfactsdesc =fetchedMars_data["marsfactsdesc"]
            marsfactsvalues =fetchedMars_data["marsfactsvalues"]
            hemisphere_image_urls = fetchedMars_data["hemisphere_image_urls"]

        else:
            title = ""
            news_paragraph = ""
            featured_image_url= "https://placeholder.com/wp-content/uploads/2018/10/placeholder.com-logo4.jpg"
            mars_weather = ""
            marsfactsdesc =""
            marsfactsvalues =""
    
        # Return template and data
        return render_template("index.html", 
                                title=title , 
                                news_paragraph=news_paragraph, 
                                featured_image_url=featured_image_url, 
                                mars_weather =mars_weather, 
                                marsfacts= zip(marsfactsdesc,marsfactsvalues),
                                hemisphere_image_urls= hemisphere_image_urls
                            )
   

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # Run the scrape function
    mars_data = scrape_mars.scrapemars_info()

    # Update the Mongo database using update and upsert=True
    mongo.db.marscollection.update({}, mars_data, upsert=True)

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
