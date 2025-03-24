import pickle
import streamlit as st
import requests
import os
import pandas as pd
import pathlib
import streamlit_authenticator as stauth
from extra_streamlit_components import CookieManager


# Initialize CookieManager with a unique key
cookie_manager = CookieManager(key="unique_cookie_manager_key")

# Load hashed passwords from file
file_path = pathlib.Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

names = ["Peter"]
usernames = ["peter"]


# Initialize Authenticate object (without cookie_manager)
cookie_name = "Mi_dashboard"  # Use the correct cookie name here
authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    cookie_name,  # Use the defined cookie name
    "abc",  # Random key for encoding
    cookie_expiry_days=30
)
# Page navigation
page = st.sidebar.radio("GO TO", ["Sign Up", "Sign in"])

if page == "Sign Up":
    # Sign-Up Form as a widget
    st.header("Create a New Account")
    new_name = st.text_input("Name")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if new_password == confirm_password:
            # Hash the new password
            new_hashed_password = stauth.Hasher([new_password]).generate()[0]
            
            # Add the new user to the credentials
            names.append(new_name)
            usernames.append(new_username)
            hashed_passwords.append(new_hashed_password)  # Append the hashed password to the list
            
            # Save the updated credentials to the file
            # Ensure hashed_passwords is a list before appending
            if isinstance(hashed_passwords, dict):
                hashed_passwords = hashed_passwords.get("hashed_passwords", [])
            
            hashed_passwords.append(new_hashed_password)  # Append the hashed password to the list
            
            # Save the updated credentials to the file
            with file_path.open("wb") as file:
                pickle.dump({"names": names, "usernames": usernames, "hashed_passwords": hashed_passwords}, file)
            
            st.success("Account created successfully! Please log in.")
        else:
            st.error("Passwords do not match.")
            st.success("Account created successfully! Please log in.")
    else:
        st.error("Passwords do not match.")

else:
    # Login widget
    name, authentication_status, username = authenticator.login("Login", "main")

    # Handle authentication status
    if authentication_status == False:
        st.error("Authentication Failed")
    if authentication_status == None:
        st.warning("Please Login")
    if authentication_status:
        # Debugging: Check if the cookie is set
        cookie_value = cookie_manager.get(cookie_name)
        if cookie_value:
            try:
                authenticator.logout("Logout", "main")
            except KeyError as e:
                st.error(f"Error during logout: {e}. Please check the cookie name.")
        else:
            st.error("Cookie not found. Please log in again.")  # Debugging statement
        
        
        # Define paths for CSV files
        feedback_csv_path = 'feedback.csv'
        watchlist_csv_path = 'watchlist.csv'
        users_csv_path = 'users.csv'

        # Ensure necessary CSV files exist
        def ensure_csv_files_exist():
            for file_path, columns in [
                (feedback_csv_path, ['user', 'movie', 'rating', 'review']),
                (watchlist_csv_path, ['user', 'movie', 'movie_id']),
                (users_csv_path, ['user', 'points', 'badge'])
            ]:
                if not os.path.exists(file_path):
                    pd.DataFrame(columns=columns).to_csv(file_path, index=False)

        ensure_csv_files_exist()

        # Load movie data
        movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
        similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
        movie_list = movies['title'].values

        st.markdown('<h1 style="text-align:center; color:#E50914;">Movie Recommendation System</h1>', unsafe_allow_html=True)
        st.subheader("🔍 Recommended Movies")

        # Ask for username first
        user_name = usernames[0]

        # Fetch movie poster
        def fetch_poster(movie_id):
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=ca601f395393a81576377be4f8230e32&language=en-US"
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                poster_path = data.get('poster_path', '')
                return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
            except requests.exceptions.RequestException:
                return "https://via.placeholder.com/500x750?text=No+Image"

        # Recommend movies
        def recommend(movie):
            if movie not in movies['title'].values:
                st.error("Selected movie not found in the database.")
                return []
            
            index = movies[movies['title'] == movie].index[0]
            distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
            
            recommendations = []
            for i in distances[1:6]:
                movie_title = movies.iloc[i[0]]['title']
                movie_id = movies.iloc[i[0]]['movie_id']
                poster = fetch_poster(movie_id)
                recommendations.append((movie_title, poster, movie_id))
            
            return recommendations

        # Add movie to watchlist
        def add_to_watchlist(user, movie, movie_id):
            try:
                # Read the existing watchlist
                df = pd.read_csv(watchlist_csv_path)
                # Check if the movie is already in the watchlist
                if ((df['user'] == user) & (df['movie_id'] == movie_id)).any():
                    st.warning(f"⚠️ {movie} is already in your watchlist!")
                    return
                
                # Append new entry and save
                new_entry = pd.DataFrame([[user, movie, movie_id]], columns=['user', 'movie', 'movie_id'])
                df = pd.concat([df, new_entry], ignore_index=True)
                df.to_csv(watchlist_csv_path, index=False)

                st.success(f"✅ {movie} added to your watchlist!")
                st.experimental_rerun()  # Force Streamlit to refresh UI
            except Exception as e:
                st.error(f"Error adding to watchlist: {e}")

        # Show watchlist
        def show_watchlist(user):
            try:
                df = pd.read_csv(watchlist_csv_path)
                return [(row['movie'], fetch_poster(row['movie_id'])) for _, row in df.iterrows() if row['user'] == user]
            except Exception as e:
                st.error(f"Error loading watchlist: {e}")
                return []

        # Show movie details
        def show_movie_details(movie_id):
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=ca601f395393a81576377be4f8230e32&language=en-US"
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                st.write(f"**Title:** {data.get('title', 'N/A')}")
                st.write(f"**Release Date:** {data.get('release_date', 'N/A')}")
                st.write(f"**Overview:** {data.get('overview', 'N/A')}")
                st.write(f"**Rating:** {data.get('vote_average', 'N/A')} / 10")
                st.write(f"**Genres:** {', '.join([genre['name'] for genre in data.get('genres', [])])}")
            except requests.exceptions.RequestException:
                st.error("Error fetching movie details.")

        # Add and show reviews
        def add_review(user, movie, rating, review):
            try:
                df = pd.read_csv(feedback_csv_path)
                new_entry = pd.DataFrame([[user, movie, rating, review]], columns=['user', 'movie', 'rating', 'review'])
                df = pd.concat([df, new_entry], ignore_index=True)
                df.to_csv(feedback_csv_path, index=False)
                st.success("✅ Review submitted!")
            except Exception as e:
                st.error(f"Error submitting review: {e}")

        def get_reviews(movie):
            try:
                df = pd.read_csv(feedback_csv_path)
                return df[df['movie'] == movie][['user', 'rating', 'review']].to_dict(orient='records')
            except Exception as e:
                st.error(f"Error loading reviews: {e}")
                return []

        # If username is entered, allow recommendations
        if user_name:
            selected_movie = st.selectbox("Type or select a Movie name", movie_list)
            
            if st.button("SHOW Recommendations"):
                recommendations = recommend(selected_movie)
                for name, poster, movie_id in recommendations:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(poster, width=120)
                    with col2:
                        st.write(name)
                        if st.button(f"➕ Add {name} to Watchlist", key=f"watchlist_{movie_id}_{user_name}"):
                            add_to_watchlist(user_name, name, movie_id)
                        with st.expander(f"ℹ️ More Info on {name}"):
                            show_movie_details(movie_id)

            # Display watchlist
            st.subheader("🎥 Your Watchlist")
            watchlist = show_watchlist(user_name)
            if watchlist:
                cols = st.columns(5)
                for idx, (movie_name, poster_url) in enumerate(watchlist):
                    with cols[idx % 5]:
                        st.image(poster_url, width=150)
                        st.write(movie_name)
            else:
                st.write("No movies added yet.")

            # Review section
            st.subheader("📝 Add Your Review")
            review_text = st.text_area("Write your review")
            rating = st.slider("Rate the movie", 1, 5, 3)
            if st.button("Submit Review"):
                add_review(user_name, selected_movie, rating, review_text)

            # Show movie reviews
            st.subheader("🎬 Reviews for Selected Movie")
            reviews = get_reviews(selected_movie)
            for rev in reviews:
                st.write(f"**{rev['user']}** ({rev['rating']}⭐): {rev['review']}")
        else:
            st.warning("Please enter your username to continue.")