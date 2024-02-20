import pandas as pd  
import streamlit as st 
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(page_title="Playlist Genrator", layout="wide",page_icon=":musical_note:")


# Read the data from the Excel file

##-------------- BACKEND------------------ ##
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="playlist.xlsx",
        engine="openpyxl",
        sheet_name="playlist",
        skiprows=0,
        usecols="A:F",
        nrows=8424,
    )
    df['track_name'] = df['track_name'].str.lower()  
    df['artist_name'] = df['artist_name'].astype(str)  # Convert artist_name to string
    return df

df = get_data_from_excel()

def get_similar_popular_tracks(track_name, df_clustering): # Function to get similar popular tracks
    
    input_track_cluster = df_clustering.loc[df_clustering["track_name"] == track_name.lower(), "Cluster"].values[0]
    input_track_popularity = df_clustering.loc[df_clustering["track_name"] == track_name.lower(), "popularity"].values[0]

    recommended_tracks = df_clustering[
        (df_clustering["Cluster"] == input_track_cluster) &
        (df_clustering["popularity"] > input_track_popularity)
    ]

    recommended_tracks = recommended_tracks.sort_values(by="popularity", ascending=False)

    recommended_track_names = recommended_tracks["track_name"].head(10).tolist()

    return recommended_track_names

## --------------FRONTEND------------------ ##


with st.container():
    st.subheader("Hi, Welcome to the playlist genrator..")
    st.write("This app utilizes the renowned Spotify dataset to generate personalized playlists based on your favorite song. Upon inputting a track name, the model identifies the cluster to which the track belongs and suggests a playlist of 10 songs from that cluster, offering users dynamically tailored playlists to match their preferences. Give it a try!"
    )
    st.write("Limitations: The dataset is restricted to a smaller number of clusters. To access the full range of clusters, it's recommended to download the dataset and execute the code on your local machine.")
    st.write("[Dataset](https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks)")
    st.write("[Check out how I am predicting the popularity of a song.](https://github.com/supragyabajpai/Playlist_Recommendation/blob/main/Code_file.ipynb)")

with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader("Look for available songs from the dataset.")

        filter_button = st.checkbox("Toggle Filters")
        filter_container = st.container()

        df_selection = df.copy()

        # If filters are toggled, show filter options
        if filter_button:
            with filter_container:
                st.write("Filters:")

                # Multiselect for genre
                genre = st.multiselect(
                    "Select the genre:",
                    options=df["genre"].unique(),
                    default=df.loc[df["genre"] == "acoustic", "genre"].unique()
                )

                # Multiselect for year
                year = st.multiselect(
                    "Select the year:",
                    options=df["year"].unique()
                )

                # Apply filters
                if genre:
                    df_selection = df_selection[df_selection["genre"].isin(genre)]
                if year:
                    df_selection = df_selection[df_selection["year"].isin(year)]

        st.write(df_selection[['artist_name', 'track_name', 'genre', 'year']], hide_index=True)



    with right_column:
        st.subheader("Enter your favourite song and get a playlist!")

        # Track recommendation
        track_name_input = st.text_input("Enter a track name:", placeholder="Yellow")

        if st.button("Get Recommendations"):
            if track_name_input:
                if track_name_input.lower() in df['track_name'].str.lower().values:
                    recommendations = get_similar_popular_tracks(track_name_input.lower(), df)
                    st.success("Recommended Tracks:")
                    
                    # Create a container to display recommended tracks as a dataframe
                    recommendations_container = st.container()

                    # Display recommended tracks dataframe
                    with recommendations_container:
                        recommendations_df = df[df['track_name'].isin(recommendations)]
                        st.dataframe(recommendations_df[['artist_name', 'track_name']], hide_index=True)
                else:
                    st.error("Track name not found in the dataset. Please make sure you are entering a valid track name.")
            else:
                st.warning("Please enter a track name.")



