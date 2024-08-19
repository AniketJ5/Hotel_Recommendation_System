from flask import Flask, request, render_template
import pickle
import pandas as pd

app = Flask(__name__)

# Load the serialized models
with open('models/user_similarity_df_train.pkl', 'rb') as f:
    user_similarity_df_train = pickle.load(f)
with open('models/item_similarity_df_train.pkl', 'rb') as f:
    item_similarity_df_train = pickle.load(f)
with open('models/content_similarity_df_train.pkl', 'rb') as f:
    content_similarity_df_train = pickle.load(f)
with open('models/user_item_matrix_train.pkl', 'rb') as f:
    user_item_matrix_train = pickle.load(f)

def get_user_based_recommendations(user_id, top_n=10):
    similar_users = user_similarity_df_train.loc[user_id].sort_values(ascending=False).head(top_n+1).index[1:]
    recommendations = user_item_matrix_train.loc[similar_users].mean().sort_values(ascending=False).head(top_n)
    return list(recommendations.items())

def get_item_based_recommendations(hotel_name, top_n=10):
    similar_items = item_similarity_df_train.loc[hotel_name].sort_values(ascending=False).head(top_n+1).index[1:]
    recommendations = user_item_matrix_train[similar_items].mean().sort_values(ascending=False).head(top_n)
    return list(recommendations.items())


def get_content_based_recommendations(hotel_name, top_n=10):
    if hotel_name in content_similarity_df_train.index:
        similarity_series = content_similarity_df_train[hotel_name]
        # Exclude the hotel itself from the list
        similarity_series = similarity_series[similarity_series.index != hotel_name]
        # Sort the similarity scores in descending order
        similar_items = similarity_series.loc[:, hotel_name].iloc[:, 1].sort_values(ascending=False).head(10).index
        l = []
        for i in similar_items:
            if i != hotel_name:
                l.append(i)

        recommendations = user_item_matrix_train[l].mean().sort_values(ascending=False).head(top_n)
        recommendations.items()
        return list(recommendations.items())
    else:
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    if request.method == 'POST':
        hotel_name = request.form['hotel_name']
        reviewer_nationality = request.form['reviewer_nationality']
        rec_type = request.form['rec_type']
        
        if rec_type == 'user':
            recommendations = get_user_based_recommendations(reviewer_nationality)
        elif rec_type == 'item':
            recommendations = get_item_based_recommendations(hotel_name)
        elif rec_type == 'content':
            recommendations = get_content_based_recommendations(hotel_name)
    
    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=4000, debug=True)
