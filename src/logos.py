import requests

# from IPython.display import Image, display
import streamlit as st
from PIL import Image
from io import BytesIO


def download_logo(team_name, logo_url):
    response = requests.get(logo_url)
    if response.status_code == 200:
        with open(f"{team_name}.png", "wb") as f:
            f.write(response.content)
            print(f"Logo downloaded: {team_name}")
        # st.image(Image(response.content))
        # image = Image.open(BytesIO(response.content))
        image = Image.open(requests.get(logo_url, stream=True).raw)
        st.image(image)

    else:
        print(f"Failed to download logo for {team_name} from {logo_url}")


TEAM_LOGOS = {
    "Manchester City WFC": "https://www.google.co.uk/url?sa=i&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FManchester_City_F.C.&psig=AOvVaw0zgK4-gW-T1YiIANBSewSj&ust=1682188967779000&source=images&cd=vfe&ved=0CBAQjRxqFwoTCIC80bDQu_4CFQAAAAAdAAAAABAE",
    "Liverpool WFC": "https://logos-world.net/wp-content/uploads/2020/06/Liverpool-Logo.png",
    "Arsenal WFC": "https://logos-world.net/wp-content/uploads/2020/05/Arsenal-Logo.png",
    "Tottenham Hotspur Women": "https://logos-world.net/wp-content/uploads/2020/05/Arsenal-Logo.png",
    "Aston Villa": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Aston_Villa_FC_crest_%282016%29.svg/1200px-Aston_Villa_FC_crest_%282016%29.svg.png",
    "Brighton & Hove Albion WFC": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fd/Brighton_%26_Hove_Albion_logo.svg/1200px-Brighton_%26_Hove_Albion_logo.svg.png",
    "Leicester City WFC": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2d/Leicester_City_crest.svg/1200px-Leicester_City_crest.svg.png"
    # Add more team names and logo URLs here
}


# for team_name, logo_url in team_logos.items():
#     download_logo(team_name, logo_url)
