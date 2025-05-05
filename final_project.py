"""
Name: Aubrey Deller
CS230: Section 4
Data: new_england_airports.csv
URL:        [Paste your Streamlit Cloud app URL here if you have it]

Description:

This program is a Streamlit web application called "New England Airports Explorer" that lets users explore airports in the New England region.
Users can filter airports by region and city, check if they offer scheduled services, and view data-driven visuals like pie charts, bar charts,
and a PyDeck map. The app features Python functions with default parameters and multiple return values, list comprehensions, error handling,
data sorting, pivot tables, and multiple Streamlit widgets for interaction.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

# [PY3]: Error checking with try/except block
try:
    # [DA1] Read and clean the data
    data = pd.read_csv('new_england_airports.csv')
    data = data.dropna(subset=['latitude_deg', 'longitude_deg'])
except FileNotFoundError:
    st.error("The dataset file could not be found. Please ensure 'new_england_airports.csv' is in the correct location.")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while loading the data: {e}")
    st.stop()

st.set_page_config(page_title="New England Airports Explorer")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Airport Filter", "Charts & Analysis", "Map & Info"])

# [ST4]: Helper function for a horizontal line with custom color
def horizontal_line(color='black'):
    st.markdown('<hr style="height:10px;border:none;color:' +
                color + ';background-color:' + color + ';" />',
                unsafe_allow_html=True)

# [PY1]: A function with two or more parameters, one of which has a default value, called at least twice (once with the value, and once without)
# [PY2]: A function that returns more than one value

def region_summary(df, region='US-CT'):
    subset = df[df['iso_region'] == region]
    count = subset.shape[0]
    max_elev = subset['elevation_ft'].max()
    return count, max_elev

count_default, elev_default = region_summary(data)
count_custom, elev_custom = region_summary(data, region='US-MA')

if page == "Airport Filter":
    st.title("Filter Airports by Region & City")
    st.header('Filter Options')

    # [ST1]: Dropdown widget
    region_list = sorted(data['iso_region'].unique())
    selected_region = st.selectbox('Select a Region (State Code):', region_list)

    region_airports = data[data['iso_region'] == selected_region]
    city_list = sorted(region_airports['municipality'].dropna().unique())
    selected_city = st.selectbox('Select a City:', city_list)

    # [ST2]: Checkbox widget
    show_scheduled_only = st.checkbox("Show only airports with scheduled service")
    if show_scheduled_only:
        region_airports = region_airports[region_airports['scheduled_service'] == 'yes']

    # [DA4]: Filter data by one condition
    st.subheader(f"Airports in {selected_region}")
    st.dataframe(region_airports[['name', 'municipality', 'type', 'scheduled_service']])

    horizontal_line('green')

    # [DA5]: Filter data by two or more conditions
    st.subheader(f"Airports in {selected_region}: {selected_city}")
    city_filtered_airports = region_airports[region_airports['municipality'] == selected_city]
    if not city_filtered_airports.empty:
        st.dataframe(city_filtered_airports[['name', 'municipality', 'type', 'elevation_ft']])
    else:
        st.write("No airports found in this city.")

elif page == "Charts & Analysis":
    st.title("Airport Charts & Insights")
    horizontal_line('blue')

    # [CHART1]: Pie chart with matplotlib
    st.header("Distribution of Airports by Region")
    region_counts = data['iso_region'].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(region_counts, labels=region_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)

    horizontal_line('teal')

    # [DA2]: Sort data
    # [DA3]: Find Top largest values
    st.header("Top 10 Highest Elevation Airports")
    top_elev = data.sort_values(by='elevation_ft', ascending=False).head(10)

    # [CHART2]: Bar chart with matplotlib
    fig3, ax3 = plt.subplots()
    ax3.barh(top_elev['name'], top_elev['elevation_ft'], color='skyblue')
    ax3.set_xlabel('Elevation (ft)')
    ax3.set_title('Highest Airports in New England')
    st.pyplot(fig3)

    horizontal_line('orange')

    # [DA6]: [DA6] Pivot table
    st.header("Pivot Table: Airport Type by Region")
    pivot = pd.pivot_table(data, index='iso_region', columns='type', aggfunc='size', fill_value=0)
    st.dataframe(pivot)

elif page == "Map & Info":
    st.title("Map of Airports & Airplane Info")

    # [MAP]: PyDeck Map with tooltip
    st.header("Map of Airports in New England")
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=data['latitude_deg'].mean(),
            longitude=data['longitude_deg'].mean(),
            zoom=5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=data,
                get_position='[longitude_deg, latitude_deg]',
                get_color='[0, 0, 255, 160]',
                get_radius=5000,
                pickable=True,
            ),
        ],
        tooltip={"text": "{name}\n{municipality}"}
    ))

    horizontal_line()

    st.subheader("Boston Logan International Airport")
    st.image("boston_logan.jpg", caption="Boston Logan International Airport", use_container_width=True)
    st.write(
        """
        Boston Logan International Airport (BOS) serves as New England’s primary air travel hub, handling tens of millions of passengers annually. 
        Located in East Boston, it offers nonstop flights across the U.S. and to major global destinations. Logan supports the region’s economy 
        by connecting New England to international business, tourism, and cargo networks. Its proximity to downtown Boston and wide range of 
        domestic and international services make it a vital part of northeastern U.S. transportation.
        """
    )

# [PY4]: A list comprehension
region_lengths = [len(region) for region in data['iso_region'].unique()]

# [DA7]: Create new columns
data['name_length'] = data['name'].apply(len)
data['high_altitude'] = data['elevation_ft'] > 2000