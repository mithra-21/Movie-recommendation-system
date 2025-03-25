movies recommender system   
The Movie Recommendation System aims to provide personalized movie suggestions to users based on their preferences. The recommendation system also displays details like the cast, crew, and overview. Here, we use a technique called content-based filtering, which recommends movies based on features such as genres, cast, crew, keywords, title, overview, movie ID, and tags that match the user's previous preferences. The system works by collecting a dataset that includes movie titles, genres, ratings, reviews, overviews, and movie IDs. After processing the data, it combines all important information into a single column and calculates the similarity between two movies based on text similarity. Along with movie suggestions, the system displays relevant movie reviews and ratings from other viewers to help users make an informed decision while also allowing them to add their own reviews. The user interacts with the system by rating movies, selecting genres they enjoy, or adding movies to their watchlist. The system also allows users to provide feedback on the recommendations, which helps refine future suggestions for them. The system also contains a prebuilt chatbot that can significantly improve user engagement, allowing users to interact naturally with the system. We also propose a movie recommendation system with gamification to make the system more interactive.

how to do-->
1.download the dataset   
2.run the ipynb_checkpoints to get  movie_list.pkl,similarity.pkl.save it in the file artifacts     
3.we use conda in powershell terminal to create a virtual environment name env     
4.use setup to create requirements and install streamlit using pip     
5.also install streamlit-authenticator==0.1.5    
