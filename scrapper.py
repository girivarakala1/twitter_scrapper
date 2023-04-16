import streamlit as st
import snscrape.modules.twitter as sntwitter
import pandas as pd
import pymongo
from bson.json_util import dumps

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://girivarkala1:Butterfly1211@cluster0.ca6tkne.mongodb.net/?retryWrites=true&w=majority")
db = client.twitter
collections = db.twitterscrap


def find_data():
    valuesList = []
    names = collections.find({})
    for res in names:
        user = res["name"]
        valuesList.append(user)
    dataList = list(set(valuesList))
    selected_name = st.selectbox("List out available keyword and hashtag stored already", dataList)
    return selected_name

def search():
    global docUpload
    option = st.radio(
        "Search with name or hashtag",
        ("name", "hashtag"))

    if option == 'name':
        name = st.text_input("Enter name to search")
    else:
        name = st.text_input("Enter hashtag")
    count = st.number_input("How many tweets needs to be scraped")
    startDate = st.date_input("Start date")
    endDate = st.date_input("End date")
    upload = st.checkbox("upload to database")
    data = "{} since:{} until:{}".format(name, startDate, endDate)
    docUpload["name"]=name
    docUpload["start date"] = startDate.isoformat()
    docUpload["end Date"] = endDate.isoformat()

    if st.button("proceed"):
        # Create an empty list to store tweet data
        tweets_list = []

        # Iterate through each tweet using snscrape and append to list
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(data).get_items()):
            if i >= count:
                break
            tweet_dict = {
                'date': tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
                'id': tweet.id,
                'url': tweet.url,

                'user': tweet.user.username,
                'reply_count': tweet.replyCount,
                'retweet_count': tweet.retweetCount,
                'language': tweet.lang,
                'source': tweet.sourceLabel,
                'like_count': tweet.likeCount
            }
            tweets_list.append(tweet_dict)
        docUpload["Scrapped Data"] = tweets_list
        doc_name = pd.DataFrame(docUpload["Scrapped Data"])
        st.dataframe(doc_name)

        if upload and name.strip():
            collections.insert_one(docUpload)




def main():
    tab1, tab2, tab3= st.tabs(["Home", "Search", "Display and download"])

    with tab1:
        st.header("from home page")

        st.write("This application helps us to scrap the data from twitter for the specific keyword or hashtag entered "
              "with given time period and number of tweets needs to be  scraped. After that, uploading the scraped data"
              "in MongoDB and downloading saved documents into Json and CSV formats", "")
    with tab2:
        st.write("you can search data  here in twitter with name or hashtag and with the upload check box data stored in mongDB")
        search()



    with tab3:
        st.write("search in database with name only available names are shown in select box . you can view and download the data here")
        data = collections.find_one({"name": find_data()})
        if data:
            data_frame = pd.DataFrame(data)
            jsonData = dumps(data, indent=2)
            csvData = pd.DataFrame(data)
            csvData.pop("_id")
            csvData = csvData.to_csv(index=False).encode('utf-8')

            if st.button("display in json"):
                st.json(data)
            if st.button("display in data table"):
                st.dataframe(data_frame)
            st.download_button(label="Download data as JSON", data=jsonData,
                              file_name="TwitterScrapData.json")
            st.download_button(label="Download data as CSV", data=csvData, file_name="TwitterScrapData.csv",
                           mime="csv")



docUpload = {}
if __name__ == '__main__':
    main()