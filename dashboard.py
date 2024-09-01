
import os
import pickle
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
from wordcloud import WordCloud
import streamlit as st

warnings.filterwarnings('ignore')

#Mengatur konfigurasi halaman Streamlit
#st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title="Fashion Muslim Industry", page_icon=":chart_with_upwards_trend:", layout="wide")
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
        background-color: #32799C; /* Background color */
        color: white; /* Text color */
        padding: 10px; /* Padding around the title */
        border-radius: 5px; /* Rounded corners */
    }
    </style>
""", unsafe_allow_html=True)
st.markdown('<p class="title">Sales Analytics</p>', unsafe_allow_html=True)

image_path = r'C:\Users\HP\Downloads\elcorps_logo.png'
st.sidebar.image(image_path, use_column_width=True)
# Custom CSS to be injected
custom_css = """
<style>
body {
    background-color: rgba(0, 0, 0, 0);  /* Transparent background */
}

[data-testid=metric-container] {
    box-shadow: 0 0 4px #f3f2f0;
    padding: 10px;
}

.plot-container>div {
    box-shadow: 0 0 2px #010101;
    padding: 5px;
    border-color: #000000;
    background-color: white; /* Make background transparent */
    border-radius: 20px; /* Rounded corners */
}

div[data-testid="stExpander"] div[role="button"] p {
    font-size: 1.2rem;
    color: rgb(0, 0, 0);
    border-color: #000000;
    color-scheme: #000000;
}

.sidebar-content {
    color: white;
}

[data-testid=stSidebar] {
    color: white;
}
</style>
"""

# Inject CSS
st.markdown(custom_css, unsafe_allow_html=True)

tab5, tab1, tab3, tab2, tab4 = st.tabs(["Product Overview", "Sales & Inventory Overview",  "Model", "Sales Forecasting", "Inventory Management"])
# Membaca data
with tab1:
    fl = st.sidebar.file_uploader("Upload a file", type=(["csv", "xlsx", 'xls']))
    if fl is not None:
        df = pd.read_csv(fl, encoding="ISO-8859-1") if fl.name.endswith('csv') else pd.read_excel(fl)
    else:
        os.chdir(r"C:\Users\HP\Desktop\streamlit")
        df = pd.read_excel(os.path.join(r"C:\Users\HP\Desktop\streamlit", "grouped_data.xlsx"))

    #col1, col2, col3, col4 = st.columns((1, 1, 1, 1))

    df["date"] = pd.to_datetime(df["date"])

    # Tanggal minimum dan maksimum
    startdate = df["date"].min()
    enddate = df["date"].max()

    # Input tanggal dari user
    date1 = st.sidebar.date_input("Start date", startdate)

    date2 = st.sidebar.date_input("End date", enddate)

    # Filter DataFrame berdasarkan tanggal
    df = df[(df["date"] >= pd.Timestamp(date1)) & (df["date"] <= pd.Timestamp(date2))].copy()
    
    
    # Sidebar untuk memilih produk dan kota
    Product = st.sidebar.multiselect("Pick the product", df["ParentName"].unique())
    if not Product:
        df2 = df.copy()
    else:
        df2 = df[df["ParentName"].isin(Product)]


    city = st.sidebar.multiselect("Pick the city", df2["City"].unique())
    if not city:
        df3 = df2.copy()
    else:
        df3 = df2[df2["City"].isin(city)]

    # DataFrame yang difilter
    if df3.empty:
        st.warning("No data available with selected filters.")
        st.stop()

    if not Product and not city:
        filtered_df = df
    elif not Product:
        filtered_df = df[df["City"].isin(city)]
    elif not city:
        filtered_df = df[df["ParentName"].isin(Product)]
    else:
        filtered_df = df[df["ParentName"].isin(Product) & df["City"].isin(city)]


    st.markdown(
                """
                <style>
                .stButton>button {
                    background-color: #0077cc !important; /* Change background color to blue */
                    color: white !important; /* Text color to white */
                    border-radius: 12px !important; /* Rounded corners */
                    padding: 8px 15px !important; /* Padding */
                    font-size: 16px !important; /* Font size */
                }

                .stButton>button:hover {
                    background-color: #005ea3 !important; /* Darken color on hover */
                }

                .stButton>button:active {
                    background-color: #005ea3 !important; /* Darken color on click */
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
    
    selected_page = st.sidebar.selectbox("Select a page", ["Sales Overview", "Inventory Overview"])
    color_map = {
        'HITAM': '#000000',
        'MERAH': '#FF2A2C',
        'BIRU': '#0068C9',
        'COKELAT': '#EFB045',
        'HIJAU': '#049E60',
        'PUTIH': '#B2B2B2',
        'UNGU' : '#F862C5',
        'KUNING': '#F8F262',
        'ORANGE': '#F2AC34',
        'red': '#FF0000',
   
                }


    if selected_page == "Sales Overview":
        # Default to 'city' if not clicked yet
 
       
        col1, col2, col3= st.columns([2, 2, 2])

        with col1:

            # Aggregate sales by city
            city_sales = filtered_df.groupby('City')['Sales'].sum().reset_index()

            # Select top 10 cities by total sales
            top10_cities = city_sales.nlargest(5, 'Sales')

            # Create a vertical bar chart
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=top10_cities['City'],
                y=top10_cities['Sales'],
                marker=dict(color='#81BEDC')
            ))

            fig.update_layout(
                title={
                    'text': "Cities with the Highest Sales",
                    'y': 0.95,
                    'x': 0.05,
                    'xanchor': 'left',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                xaxis_title='City',
                yaxis_title='Total Sales',
                hovermode='closest',
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color='white'),
                clickmode='event+select',
                height=300,
                margin=dict(l=0, r=0, t=50, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            col1, col2 = st.columns((1,1))
            with col1:

                color_top5 = filtered_df.pivot_table(index='ColorParentName', values='Sales', aggfunc='sum').sort_values(by='Sales', ascending=False)
                df_pie = color_top5.reset_index()

                

                fig = go.Figure(data=[go.Pie(
                    labels=df_pie['ColorParentName'],
                    values=df_pie['Sales'],
                    hole=0.5,  # Creates the donut chart
                    pull=[0, 0, 0, 0, 0],  # Highlights the 'rust' section
                    textinfo='label+value',
                    marker=dict(colors = [color_map[color] for color in df_pie['ColorParentName']]),
                    hoverinfo='label+percent+name',  # Add more hover information
                )])
                fig.update_layout(
                    title={
                        'text': "Best Selling Color",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': dict(size=20, color='black', family="Open Sans")
                    },
                    showlegend=False,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bordercolor='gray',
                        borderwidth=1
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                    plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
                    font=dict(color='white'),  # White font color
                    clickmode='event+select',
                    height=300,
                    margin=dict(l=20, r=20, t=50, b=20)
                )

                # Display the figure
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                colorcode_top5 = filtered_df.pivot_table(index='Color Code', values='Sales', aggfunc='sum').sort_values(by='Sales', ascending=False)
                df_pie = colorcode_top5.reset_index()

                fig = go.Figure(data=[go.Pie(
                    labels=df_pie['Color Code'],
                    values=df_pie['Sales'],
                    hole=0.5,  # Creates the donut chart
                    pull=[0, 0, 0, 0, 0],  # Highlights the 'rust' section
                    textinfo='label+value',
                    # marker=dict(colors=[color_map[color] for color in df_pie['ColorParentName']]),
                    hoverinfo='label+percent+name',  # Add more hover information
                )])
                fig.update_layout(
                    title={
                        'text': "Best Selling Color",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': dict(size=20, color='black', family="Open Sans")
                    },
                    showlegend=False,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bordercolor='gray',
                        borderwidth=1
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                    plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
                    font=dict(color='white'),  # White font color
                    clickmode='event+select',
                    height=300,
                    margin=dict(l=20, r=20, t=50, b=20)
                )

                # Display the figure
                st.plotly_chart(fig, use_container_width=True)
            


        with col3:
            city_color_sales = filtered_df.groupby(['City', 'ColorParentName'])['Sales'].sum().reset_index()
            total_sales_by_city = city_color_sales.groupby('City')['Sales'].sum()

            # Calculate percentage for each color within each city
            city_color_sales['Percentage'] = city_color_sales.apply(lambda x: (x['Sales'] / total_sales_by_city[x['City']]) * 100, axis=1)

            # Filter top cities and colors
            top10_cities = total_sales_by_city.nlargest(10).index
            top5_colors = city_color_sales.groupby('ColorParentName')['Sales'].sum().nlargest(5).index

            # Filter and sort data for top cities and colors
            city_color_sales_top = city_color_sales[(city_color_sales['City'].isin(top10_cities)) & (city_color_sales['ColorParentName'].isin(top5_colors))]
            city_color_sales_top = city_color_sales_top.sort_values(by=['City', 'Percentage'], ascending=[True, False])

            # Create a dictionary to map colors to unique indices for consistent coloring

            # Initialize figure
            fig = go.Figure()

            # Add bars for each city and color
            for city in top10_cities:
                df_city = city_color_sales_top[city_color_sales_top['City'] == city]
                bars = []
                for index, row in df_city.iterrows():
                    color = row['ColorParentName']
                    bars.append(go.Bar(
                        y=[city],
                        x=[row['Percentage']],
                        name=color,
                        text=[f"{row['Percentage']:.2f}%"],
                        orientation='h',
                        marker=dict(color=color_map[color], line=dict(width=0.3))
                    ))
                fig.add_traces(bars)

            # Update layout
            fig.update_layout(
                title ={ 
                    'text': "Sales by Color in Top 5 Cities",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                    },
                yaxis_title='City',
                xaxis_title='Percentage (%)',
                barmode='stack',
                hovermode='closest',
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color='white'),
                clickmode='event+select',
                height=300,
                margin=dict(l=10, r=10, t=50, b=0),
                showlegend=False,
                yaxis=dict(autorange='reversed', dtick=1),
            )

            fig.update_yaxes(fixedrange=False)

            # Display the plot in Streamlit
            st.plotly_chart(fig, use_container_width=True)

    
        


    
        col4, col5, col6 = st.columns((1,1,3))
    
        with col4:
            Store_Top5 = filtered_df.pivot_table(index='StoreCode', values='Sales', aggfunc='sum').sort_values(by='Sales', ascending=False).head(5)
            df_StoreCode = Store_Top5.reset_index()
            fig = go.Figure(data=[go.Pie(
                labels=df_StoreCode['StoreCode'],
                values=df_StoreCode['Sales'],
                hole=.5,  # Creates the donut chart
                pull=[0, 0, 0, 0, 0],  # Highlights the 'rust' section
                textinfo='label+value',
                marker=dict(
                    colors=['#32799C', '#4290B7', '#56A8D0', '#6BB5DA', '#81BEDC','97CDE8', 'AFDBF1', 'C5DFEC', 'D8E8F1' ]
                ),
                hoverinfo='label+percent+name',  # Add more hover information
            )])
            fig.update_layout(
                title={
                    'text': "Top 5 Stores",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                showlegend=False,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bordercolor='gray',
                    borderwidth=1
                ),
                paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
                font=dict(color='white'),  # White font color
                clickmode='event+select',
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )

            # Display the figure
            st.plotly_chart(fig, use_container_width=True)
       
        with col5:
            product_top5 = filtered_df.pivot_table(index='ProductName', values='Sales', aggfunc='sum').sort_values(by='Sales', ascending=False)
            df_ProductName = product_top5.reset_index()
            fig = go.Figure(data=[go.Pie(
                labels=df_ProductName['ProductName'],
                values=df_ProductName['Sales'],
                hole=.5,  # Creates the donut chart
                pull=[0, 0, 0, 0, 0],  # Highlights the 'rust' section
                textinfo='label+value',
                marker=dict(
                    colors=['#32799C', '#4290B7', '#56A8D0', '#6BB5DA', '#81BEDC','97CDE8', 'AFDBF1', 'C5DFEC', 'D8E8F1' ]
                ),
                hoverinfo='label+percent+name',  # Add more hover information
            )])
            fig.update_layout(
                title={
                    'text': "Sales by Product",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                showlegend=False,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bordercolor='gray',
                    borderwidth=1
                ),
                paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
                font=dict(color='white'),  # White font color
                clickmode='event+select',
                height=300,
                margin=dict(l=20, r=20, t=70, b=20)
            )

            # Display the figure
            st.plotly_chart(fig, use_container_width=True)

        with col6:

            def generate_word_cloud(data_dict, title):
                # Generate word cloud
                wordcloud = WordCloud(width=800, height=300, background_color='white', colormap = 'PuBu').generate_from_frequencies(data_dict)

                # Display the word cloud using matplotlib
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')

                # Add a rectangle border around the word cloud
                rect = Rectangle((0, 0), 1, 1, linewidth=0.5, edgecolor='blue', facecolor='none', transform=ax.transAxes, clip_on=False, zorder=50)
                rect.set_clip_path(ax.patch)
                ax.add_patch(rect)

                # Use Streamlit to display the word cloud
                st.pyplot(fig)


            city_sales = filtered_df.groupby('City')['Sales'].sum().to_dict()
            Store_sales = filtered_df.groupby('StoreCode')['Sales'].sum().to_dict()
            Color_sales = filtered_df.groupby('Color Code')['Sales'].sum().to_dict()

            
            # Layout
            col1, col2= st.columns((9,1))
            st.markdown(
                """
                <style>
                .stButton>button {
                    width: 100% !important; /* Make the button fit the column width */
                    background-color: #0077cc !important; /* Change background color to blue */
                    color: white !important; /* Text color to white */
                    border-radius: 12px !important; /* Rounded corners */
                    padding: 8px 15px !important; /* Padding */
                    font-size: 16px !important; /* Font size */
                    margin-bottom: 20px !important;
                }

                .stButton>button:hover {
                    background-color: #005ea3 !important; /* Darken color on hover */
                }

                .stButton>button:active {
                    background-color: #005ea3 !important; /* Darken color on click */
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            with col2:
                city_clicked = st.button("City", key="city")
                store_clicked = st.button("Store", key="store")
                color_clicked = st.button("Color", key="color")
            
            with col1:
            
                # Generate the word cloud based on the button clicked
                if city_clicked:
                    generate_word_cloud(city_sales, "City Sales Word Cloud")
                elif store_clicked:
                    generate_word_cloud(Store_sales, "Store Sales Word Cloud")
                elif color_clicked:
                    generate_word_cloud(Color_sales, "Color Sales Word Cloud")
                else:
                    # If no button is clicked, generate the City Sales Word Cloud by default
                    generate_word_cloud(city_sales, "City Sales Word Cloud")
       


        df_prodgrade = filtered_df.copy()
     
        def classify_sales(sales):
            if 60 <= sales <= 385:
                return 'A'
            elif 14 <= sales <= 59:
                return 'B'
            elif 1 <= sales <= 13:
                return 'C'
            else:
                return 'undefined'

        # Membuat kolom baru 'Product_Grade'
        df_prodgrade['Product_Grade'] = df_prodgrade['Sales'].apply(classify_sales)
        top_sales = df_prodgrade.nlargest(10, 'Sales')

        st.table(top_sales)


        selected_store_code = st.multiselect("Filter the Store", df_prodgrade['StoreCode'].unique())
        columns_to_show = ['ParentName', 'Color Code', 'Sales', 'Product_Grade']

        if not selected_store_code:
            st.table(df_prodgrade[columns_to_show].nlargest(10, 'Sales'))
        else:
            filtered_df_prodgrade=df_prodgrade[df_prodgrade['StoreCode'].isin(selected_store_code)]
            st.table(filtered_df_prodgrade[columns_to_show].nlargest(10, 'Sales'))
        

    elif selected_page == "Inventory Overview":
        col1, col2, col3, = st.columns((1,1,2))

        with col1:
            Total_inventory = filtered_df['Inventory'].sum()
            Total_SKU = filtered_df['SKU'].nunique()
            fixed_height = 140
            st.markdown(f"""
                <style>
                .card {{
                    background-color: #4290B7;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    font-family: Arial, sans-serif;
                    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                    height: {fixed_height}px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    margin: 10px;
                
                }}
                .Total-SKU {{
                    font-size: 100px;
                    font-weight: bold;
                    color: white;
                }}
                .percentage {{
                    font-size: 10px;
                    color: green;
                }}
                </style>
                <div class="card">
                    <div class="total-sales">{Total_inventory}</div>
                    <div class="total-sales">Total Inventory</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <style>
                .card {{
                    background-color: #4290B7;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    font-family: Arial, sans-serif;
                    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                    height: {fixed_height}px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    margin: 10px;
                
                }}
                .Total-SKU {{
                    font-size: 100px;
                    font-weight: bold;
                    color: white;
                }}
                .percentage {{
                    font-size: 10px;
                    color: green;
                }}
                </style>
                <div class="card">
                    <div class="total-sales">{Total_SKU}</div>
                    <div class="total-sales">Total SKU</div>
                </div>
                </div>
            """, unsafe_allow_html=True)

        with col2:

            status_counts = filtered_df['Status'].value_counts().reset_index()
            status_counts['percent'] = status_counts['count'] / status_counts['count'].sum() * 100
            
            fig = go.Figure(data=[go.Pie(
                    labels=status_counts['Status'],
                    values=status_counts['percent'],
                    hole=.5,  # Creates the donut chart
                    pull=[0, 0, 0, 0, 0],  # Highlights the 'rust' section
                    textinfo='label+value',
                    marker=dict(
                        colors=['#32799C', '#4290B7', '#56A8D0', '#6BB5DA', '#81BEDC','97CDE8', 'AFDBF1', 'C5DFEC', 'D8E8F1' ]
                    ),
                    hoverinfo='label+percent+name',  # Add more hover information
                    textfont=dict(size=15),
                )])
            fig.update_layout(
                title={
                    'text': "Inventory Status",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                showlegend=False,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bordercolor='gray',
                    borderwidth=1
                ),
                paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
                font=dict(color='white'),  # White font color
                clickmode='event+select',
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )

            # Forecasted Accuracy
            st.plotly_chart(fig, use_container_width=True)

            # with col2:
            #     Overstock_color = filtered_df.groupby(['Color Code'])['Inventory'].sum().reset_index()
            #     top10_Overstock = Overstock_color.nlargest(10, 'Inventory')

            #     fig = go.Figure(data=[go.Pie(
            #     labels=top10_Overstock['Color Code'],
            #     values=top10_Overstock['Inventory'],
            #     hole=.6,  # Creates the donut chart
            #     pull=[0, 0, 0, 0, 0],  # Highlights the 'rust' section
            #     textinfo='label+value',
            #     marker=dict(
            #         colors=['#32799C', '#4290B7', '#56A8D0', '#6BB5DA', '#81BEDC','97CDE8', 'AFDBF1', 'C5DFEC', 'D8E8F1' ]
            #     ),
            #     hoverinfo='label+percent+name',  # Add more hover information
            #     )])
            #     fig.update_layout(
            #         title={
            #             'text': "Highest Overstock Rates by Color",
            #             'y': 0.95,
            #             'x': 0.5,
            #             'xanchor': 'center',
            #             'yanchor': 'top',
            #             'font': dict(size=20, color='black', family=" Open Sans")
            #         },
            #         showlegend=False,
            #         legend=dict(
            #             orientation="h",
            #             yanchor="bottom",
            #             y=1.02,
            #             xanchor="right",
            #             x=1,
            #             bordercolor='gray',
            #             borderwidth=1
            #         ),
            #         paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
            #         plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
            #         font=dict(color='white'),  # White font color
            #         clickmode='event+select',
            #         height=300,
            #         margin=dict(l=20, r=20, t=50, b=20)
            #     )
            #     st.plotly_chart(fig, use_container_width=True)


            # print(status_counts)
                
        with col3:
                
                # Assuming filtered_df is your filtered dataframe
                # Group by ParentName for Product chart
                Total_inventory_parent = filtered_df.groupby(['ParentName'])['Inventory'].sum().reset_index()
                sales_by_parent = filtered_df.groupby(['ParentName'])['Sales'].sum().reset_index()

                # Group by Color Code for Color chart
                Inventory_co = filtered_df.groupby(['Color Code'])['Inventory'].sum().reset_index()
                Inventory_color = Inventory_co.nlargest(10, 'Inventory')
                sales_color = filtered_df.groupby(['Color Code'])['Sales'].sum().reset_index()
                merge_inv = Inventory_color.merge(sales_color, on='Color Code', how='left')

                # Group by City for City chart
                Inventory_City = filtered_df.groupby(['City'])['Inventory'].sum().reset_index()
                df_Inventory_City = Inventory_City.nlargest(10, 'Inventory')
                sales_City = filtered_df.groupby(['City'])['Sales'].sum().reset_index()
                merge_city = df_Inventory_City.merge(sales_City, on='City', how='left')

                # Create the chart based on the selected type
                
             
    
                fig = go.Figure(data=[
                    go.Bar(
                        name='Inventory by City',
                        x=merge_city['City'].astype(str),
                        y=merge_city['Inventory'],
                        marker=dict(color='#32799C'),
                        text=merge_city['Inventory'],
                        textposition='auto',
                        offsetgroup=0
                    ),
                    go.Bar(
                        name='Sales by City',
                        x=merge_city['City'].astype(str),
                        y=merge_city['Sales'],
                        marker=dict(color='#97CDE8'),
                        text=merge_city['Sales'],
                        textposition='auto',
                        offsetgroup=0
                    )
                ])
                fig.update_layout(

                    title={
                        'text': "Top 10 Inventory and Sales by City",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': dict(size=20, color='black', family="Open Sans")
                    },
                    xaxis_title="Category",
                    yaxis_title="Value",
                    barmode='group',
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color='black'),
                    height=300,
                    margin=dict(l=0, r=0, t=50, b=0),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=-0.5,
                        xanchor='right',
                        x=1
                        
                    )
                )

                fig.update_xaxes(type='category')
                st.plotly_chart(fig, use_container_width=True)
                    
        col1, col2 = st.columns((2,2))
        with col2:
            fig = go.Figure(data=[
                go.Bar(
                    name='Inventory by Color',
                    x=merge_inv['Color Code'].astype(str),
                    y=merge_inv['Inventory'],
                    marker=dict(color='#32799C'),
                    text=merge_inv['Inventory'],
                    textposition='auto',
                    offsetgroup=0
                ),
                go.Bar(
                    name='Sales by Color',
                    x=merge_inv['Color Code'].astype(str),
                    y=merge_inv['Sales'],
                    marker=dict(color='#97CDE8'),
                    text=merge_inv['Sales'],
                    textposition='auto',
                    offsetgroup=0
                )
            ])
            fig.update_layout(
                title={
                    'text': "Top 10 Inventory and Sales by Color",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                xaxis_title="Category",
                yaxis_title="Value",
                barmode='group',
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color='black'),
                height=350,
                margin=dict(l=0, r=0, t=50, b=0),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=-0.3,
                    xanchor='right',
                    x=1
                )
            )

            fig.update_xaxes(type='category')
            st.plotly_chart(fig, use_container_width=True)
        with col1:
            fig = go.Figure(data=[
               
                go.Bar(
                    name='Inventory by Product',
                    x=Total_inventory_parent['ParentName'].astype(str),
                    y=Total_inventory_parent['Inventory'],
                    marker=dict(color='#32799C'),
                    text=Total_inventory_parent['Inventory'],
                    textposition='auto',
                    offsetgroup=0
                ),
                go.Bar(
                    name='Sales by Product',
                    x=sales_by_parent['ParentName'].astype(str),
                    y=sales_by_parent['Sales'],
                    marker=dict(color='#97CDE8'),
                    text=sales_by_parent['Sales'],
                    textposition='auto',
                    offsetgroup=0
                )
            ])
            fig.update_layout(
                title={
                    'text': "Inventory and Sales by Product",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                xaxis_title="Category",
                yaxis_title="Value",
                barmode='group',
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color='black'),
                height=350,
                margin=dict(l=0, r=0, t=50, b=0),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=-0.3,
                    xanchor='right',
                    x=1
                )
            )
            fig.update_xaxes(type='category')
            st.plotly_chart(fig, use_container_width=True)


        timeseries_inventory = df.groupby(['date'])['Inventory'].sum().reset_index()

        timeseries_sales = df.groupby(['date'])['Sales'].sum().reset_index()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=timeseries_inventory['date'],
            y=timeseries_inventory['Inventory'],
            mode='lines+markers',
            name='Inventory',
            line=dict(color='#0077cc', width=2),
            marker=dict(color='#0077cc', size=8),
            text=timeseries_inventory['Inventory'],
            hoverinfo='text+y'
        ))
        fig.add_trace(go.Scatter(
            x=timeseries_sales['date'],
            y=timeseries_sales['Sales'],
            mode='lines+markers',
            name='Sales',
            line=dict(color='#cc0000', width=2),
            marker=dict(color='#cc0000', size=8),
            text=timeseries_sales['Sales'],
            hoverinfo='text+y'
        ))
        # Update layout
        fig.update_layout(
            title={
                        'text': "Time Series of Inventory",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': dict(size=20, color='black', family="Open Sans")
                    },
            xaxis_title='Date',
            yaxis_title='Inventory',
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color='black'),
            height=300,
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='right',
                x=1
            )
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

            

            




with tab3:
    pf = st.file_uploader("Upload a file", type=(["csv", "xlsx", 'xls']), key="file predictions")
    if pf is not None:
        df_pf = pd.read_csv(pf, encoding="ISO-8859-1") if pf.name.endswith('csv') else pd.read_excel(pf)
    else:
        os.chdir(r"C:\Users\HP\Desktop\streamlit")
        df_pf = pd.read_excel(os.path.join(r"C:\Users\HP\Desktop\streamlit", "for_predictions.xlsx"))

    # Drop 'date' column if it exists
    if 'date' in df_pf.columns:
        df_pf.drop(columns=['date'], inplace=True)

    # Create a copy of the original dataframe for encoding
    df_encoding = df_pf.copy()

    # Encode categorical columns
    label_encoder = LabelEncoder()
    categorical_columns = ['StoreCode', 'StoreGrade', 'ColorParentName', 'Province', 'ParentName', 'ProductName', 'City', 'ProductGrade']
    for col in categorical_columns:
        if col in df_encoding.columns:
            df_encoding[col] = label_encoder.fit_transform(df_encoding[col])

    # Ensure all columns have the correct data type
    df_encoding = df_encoding.apply(pd.to_numeric, errors='coerce')

    # Apply log transformation to the Inventory column
    df_encoding['Inventory'] = np.log1p(df_encoding['Inventory'])

    # Load model and make predictions
    model = pickle.load(open("best_model_xgb.pkl", "rb"))
    predict = model.predict(df_encoding)

    # Inverse log transformation of predictions
    predictions_inverse = np.exp(predict)
    predictions_inverse_df = pd.DataFrame(predictions_inverse, columns=['Sales Predictions'])

    # Create a copy of the original dataframe to store predictions
    predictions_df = df_pf.copy()
    predictions_df['Sales Predictions'] = predictions_inverse_df['Sales Predictions']

    # Display the dataframe with original columns and predictions
    st.dataframe(predictions_df)


    #buat ngitung akurasi
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    df_akurasi = pd.read_excel(os.path.join(r"C:\Users\HP\Desktop\streamlit", "grouped_data_no_encoding.xlsx"))
    df_akurasi = df_akurasi[df_akurasi['Inventory'] > -1]


    df_akurasi['StoreCode'] = label_encoder.fit_transform(df_akurasi['StoreCode'])
    df_akurasi['StoreGrade'] = label_encoder.fit_transform(df_akurasi['StoreGrade'])
    df_akurasi['ColorParentName'] = label_encoder.fit_transform(df_akurasi['ColorParentName'])
    df_akurasi['Province'] = label_encoder.fit_transform(df_akurasi['Province'])
    df_akurasi['ParentName'] = label_encoder.fit_transform(df_akurasi['ParentName'])
    df_akurasi['ProductName'] = label_encoder.fit_transform(df_akurasi['ProductName'])
    df_akurasi['City'] = label_encoder.fit_transform(df_akurasi['City'])
    df_akurasi['ProductGrade'] = label_encoder.fit_transform(df_akurasi['ProductGrade'])
    df_akurasi['SKU'] = label_encoder.fit_transform(df_akurasi['SKU'])

    df_akurasi['Sales'] = np.log1p(df_akurasi['Sales'])  # np.log1p digunakan untuk menghindari masalah dengan nilai nol
    df_akurasi['Inventory'] = np.log1p(df_akurasi['Inventory'])


    x = df_akurasi[['Year', 'Month', 'StoreCode',  'Color Code', 'StoreGrade', 'ColorParentName', 'Province', 'ParentName',  'ProductName', 'City', 'ProductGrade', 'SKU','GrossSales' ,'Inventory']]
    y = df_akurasi[['Sales']]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.35, random_state=42)
    y_pred_train = model.predict(x_train)
    y_pred_test = model.predict(x_test)

    r21 = r2_score(y_train,y_pred_train)
    r22 = r2_score(y_test, y_pred_test)

    col1, col2 = st.columns((2, 7))

    with col2:
        st.dataframe(predictions_df)
    

    with col1:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = r22,
            title = {'text': "Forecast Accuracy"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 50], 'color': "#97CDE8"},
                    {'range': [50, 100], 'color': "#32799C"}
                ],
            }
        ))
        fig.update_layout(
            autosize=True,
            height=250,  # Adjust height as needed
            margin=dict(l=20, r=20, t=50, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)


    

    #st.write("Prediction:", predict)

with tab2:


    col1, col2 = st.columns((1.5,6))
    
    total_sales_predictions = round(predictions_df['Sales Predictions'].sum())
    total_sales_actual = filtered_df['Sales'].sum()
    percentage_actual_vs_predicted = ((total_sales_predictions-total_sales_actual)/total_sales_actual)* 100
    
    fixed_height = 160
    with col1:
        Best_Color_Predictions = predictions_df.pivot_table(index='Color Code', values='Sales Predictions', aggfunc='sum').sort_values(by='Sales Predictions', ascending=False)
        df_pie_predictions = Best_Color_Predictions.reset_index().round(0)

        fig = go.Figure(data=[go.Pie(
            labels=df_pie_predictions['Color Code'],
            values=df_pie_predictions['Sales Predictions'],
            hole=.3,  # Creates the donut chart
            pull=[0, 0, 0, 0, 0],  # Highlights the 'rust' section
            textinfo='label+value',
            # marker=dict(colors=[color_map[color] for color in df_pie_predictions['Color Code']]),  # Assign colors to pie sections
            hoverinfo='label+percent+name',  # Add more hover information
        )])
        fig.update_layout(
            title={
                'text': "Sales Predictions by Color Code",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=20, color='black', family="Open Sans")
            },
            showlegend=False,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bordercolor='gray',
                borderwidth=1
            ),
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
            font=dict(color='white'),  # White font color
            clickmode='event+select',
            height=300,
            margin=dict(l=20, r=20, t=70, b=20)
        )

        # Forecasted Accuracy
        st.plotly_chart(fig, use_container_width=True)


        
        st.markdown(f"""
            <style>
            .card1 {{
                background-color: #4290B7;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                font-family: Arial, sans-serif;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                height: {fixed_height}px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                margin: 10px;
            
            }}
            .total-sales {{
                font-size: 15px;
                font-weight: bold;
                color: white;
            }}
            .percentage {{
                font-size: 10px;
                color: white;
            }}
            </style>
            <div class="card1">
                <div class="total-sales">Total Actual Sales: {total_sales_actual}</div>
            </div>
        """, unsafe_allow_html=True)
    
        arrow = "↑" if percentage_actual_vs_predicted > 0 else ""
        color = "white" if percentage_actual_vs_predicted > 0 else "red"
        st.markdown(f"""
            <style>
            .card2 {{
                background-color: #DC3545;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                font-family: Arial, sans-serif;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                height: {fixed_height}px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                margin: 10px;
            }}
            .total-sales {{
                font-size: 18px;
                font-weight: bold;
            }}
            .percentage {{
                font-size: 10px;
                font-weight: bold;
                color: white;
            }}
            </style>
            <div class="card2">
                <div class="total-sales">Total Predicted Sales: {total_sales_predictions}</div>
                <div class="percentage">{arrow} {percentage_actual_vs_predicted:.2f}% of Actual Sales</div>
            </div>
        """, unsafe_allow_html=True)
   
        st.markdown(f"""
            <style>
            .card3 {{
                background-color: #198754;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                font-family: Arial, sans-serif;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                height: {fixed_height}px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                margin: 10px;
            
            }}
            .total-sales {{
                font-size: 15px;
                font-weight: bold;
            }}
            .percentage {{
                font-size: 10px;
                color: white;
            }}
            </style>
            <div class="card3">
                <div class="total-sales">Raw Material Needed: {total_sales_actual}</div>
            </div>
        """, unsafe_allow_html=True)


    

    
    with col2:
        col1, col2, col3 = st.columns((1,1,1))
        with col1:
            Best_Color_Predictions = predictions_df.pivot_table(index='ColorParentName', values='Sales Predictions', aggfunc='sum').sort_values(by='Sales Predictions', ascending=False)
            df_pie_predictions = Best_Color_Predictions.reset_index().round(0)

            fig = go.Figure(data=[go.Pie(
                labels=df_pie_predictions['ColorParentName'],
                values=df_pie_predictions['Sales Predictions'],
                hole=.3,  # Creates the donut chart
                pull=[0, 0, 0, 0, 0],  # Highlights the 'rust' section
                textinfo='label+value',
                marker=dict(colors=[color_map[color] for color in df_pie_predictions['ColorParentName']]),  # Assign colors to pie sections
                hoverinfo='label+percent+name',  # Add more hover information
            )])
            fig.update_layout(
                title={
                    'text': "Sales Predictions by Color",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                showlegend=False,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bordercolor='gray',
                    borderwidth=1
                ),
                paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
                font=dict(color='white'),  # White font color
                clickmode='event+select',
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )

            # Forecasted Accuracy
            st.plotly_chart(fig, use_container_width=True)

        with col2:
    # sales predict by color code
            top_color_code_actual = filtered_df.groupby(['Color Code'])['Sales'].sum().reset_index()
            top_color_code_actual['Color Code'] = top_color_code_actual['Color Code'].astype(str)

            top_color_code_predictions = predictions_df.groupby(['Color Code'])['Sales Predictions'].sum().reset_index()
            top_color_code_predictions['Color Code'] = top_color_code_predictions['Color Code'].astype(str)
            
            df_top_color_code_predictions = top_color_code_predictions.nlargest(5, 'Sales Predictions')
            df_hist_color_code = df_top_color_code_predictions.merge(top_color_code_actual, on='Color Code', how='left').round(0)
            

        
            fig = go.Figure(data=[
                
                go.Bar(
                    name='Sales',
                    x=df_hist_color_code['Color Code'].astype(str),
                    y=df_hist_color_code['Sales'],
                    marker=dict(color='#97CDE8'),
                    text=df_hist_color_code['Sales'],  # Add text to show the exact value on hover
                    textposition='auto',
                    offsetgroup=1
                ),

                go.Bar(
                    name='Sales Predictions',
                    x=df_hist_color_code['Color Code'].astype(str),
                    y=df_hist_color_code['Sales Predictions'],
                    marker=dict(color='#32799C'),
                    text=df_hist_color_code['Sales Predictions'],  # Add text to show the exact value on hover
                    textposition='auto',  # Automatically decide where to show the text
                    offsetgroup=0
                )
            ])

            # Update layout
            fig.update_layout(
                title={
                    'text': "Sales Predictions by Color Code",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                xaxis_title="Color Code",
                yaxis_title="Value",
                barmode='group',  # Groups the bars together
                paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
                font=dict(color='black'),  # Black font color
                height=300,
                margin=dict(l=0, r=0, t=50, b=0),
                legend=dict(
                    orientation='h',  # Horizontal orientation
                    yanchor='bottom',  # Anchor legend to the bottom
                    y=-0.1,  # Position above the plot
                    xanchor='right',
                    x=1
                )
            )

            fig.update_xaxes(type='category')

            # Display the bar chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

        with col3:

            total_sales_by_store = predictions_df.groupby(['StoreCode'])['Sales Predictions'].sum().reset_index()
            ranked_store = total_sales_by_store
            ranked_store['SalesRank'] = ranked_store['Sales Predictions'].rank(ascending=False, method='min').astype(int)

            # Menghitung penjualan aktual total per toko dan peringkatnya
            total_sales_by_store_actual = filtered_df.groupby(['StoreCode'])['Sales'].sum().reset_index()
            total_sales_by_store_actual['SalesRankActual'] = total_sales_by_store_actual['Sales'].rank(ascending=False, method='min').astype(int)

            # Menggabungkan data prediksi dan aktual berdasarkan StoreCode
            df_ranked_store = ranked_store.merge(total_sales_by_store_actual, on='StoreCode', how='left')
            df_ranked_store['Rank_Change'] = (df_ranked_store['SalesRankActual'] - df_ranked_store['SalesRank']).fillna(0).astype(int)

            def generate_row_html(rank_change, store):
                color = "#0068C9"  # Warna latar belakang untuk kotak
                html = f"""
                <div style="display: flex; align-items: center; justify-content: center; margin: 5px 0; ">
                    <div style="background-color: {color}; color: white; padding: 10px; text-align: center; flex: 1;">
                        {rank_change}
                    </div>
                    <div style="background-color: {color}; color: white; padding: 10px; margin-left: 10px; width: 100px; text-align: center; flex: 3;">
                        {store}
                    </div>
                </div>
                """
                return html

            def generate_container_html(rows_html):
                container_html = """
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 12px; height: 300px; overflow-y: auto">
                    <h1 style="font-size: 20px; text-align: center; margin-top: 0; padding-top: 0; ">Store ranking</h1>
                    {}
                </div>
                """.format("".join(rows_html))
                return container_html

            # Menghasilkan HTML untuk semua baris
            rows_html = [generate_row_html(f"{int(row['Rank_Change']):+d}", row['StoreCode']) for index, row in df_ranked_store.iterrows()]

            # Menghasilkan HTML kontainer
            container_html = generate_container_html(rows_html)

        # Menampilkan kontainer di Streamlit
            st.markdown(container_html, unsafe_allow_html=True)           
            # title_html = """
            # <h1 style="font-size: 14px;">Store ranking</h1>
            # """

            # st.title("Store ranking")
            # print(df_ranked_store)

            # # Generate and display the HTML for each row in the DataFrame
            # for index, row in df_ranked_store.iterrows():
            #     rank_change = f"{row['Rank_Change']:+d}"
            #     store = row['StoreCode']
            #     st.markdown(generate_row_html(rank_change, store), unsafe_allow_html=True)


           
        col1, col2 = st.columns((1, 2))

        with col1:
            top_produt_actual = filtered_df.groupby(['ProductName'])['Sales'].sum().reset_index()
            top_produt_actual1 = top_produt_actual.nlargest(10, 'Sales')
            top_product_pred = predictions_df.groupby(['ProductName'])['Sales Predictions'].sum().reset_index()
            top_product_pred1 = top_product_pred.round(0)
            st.markdown(
                '''
                <p class="section-header" style="text-align: center; background-color: #4290B7; font-weight: bold; color: white; border-radius: 10px; padding: 10px;">
                    Product Priority
                </p>
                ''',
                unsafe_allow_html=True
            )
            st.dataframe(top_product_pred1)
            #st.table(top_produt_actual1)
        


        with col2:
        #Sales predictions by city

            sales_actual_by_city = filtered_df.groupby(['City'])['Sales'].sum().reset_index()

            sales_predicted_by_city = predictions_df.groupby(['City'])['Sales Predictions'].sum().reset_index()
            df_sales_predicted_by_city = sales_predicted_by_city.nlargest(5, 'Sales Predictions')

            df_sales_predicted_by_city_graph = df_sales_predicted_by_city.merge(sales_actual_by_city, on='City', how='left')

            print(df_sales_predicted_by_city_graph)
            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=df_sales_predicted_by_city_graph['City'],
                x=df_sales_predicted_by_city_graph['Sales'],
                orientation='h',
                name='Histori Penjualan',
                marker=dict(color='#97CDE8'),
                text=df_sales_predicted_by_city_graph['Sales'],
                textposition='auto'
            ))

            fig.add_trace(go.Bar(
                y=df_sales_predicted_by_city_graph['City'],
                x=df_sales_predicted_by_city_graph['Sales Predictions'],
                orientation='h',
                name='Prediksi Penjualan',
                marker=dict(color='#32799C'),
                text=df_sales_predicted_by_city_graph['Sales Predictions'],
                textposition='auto'
            ))

            # Update layout
            fig.update_layout(
                title={
                    'text': "Sales Predictions by City",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=20, color='black', family="Open Sans")
                },
                xaxis_title="Sales",
                yaxis_title="City",
                barmode='group',  # Groups the bars together
                paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent plot background
                font=dict(color='black'),  # Black font color
                height=450,
                margin=dict(l=0, r=0, t=50, b=0),
                legend=dict(
                    orientation='h',  # Horizontal orientation
                    yanchor='bottom',  # Anchor legend to the bottom
                    y=0,  # Position above the plot
                    xanchor='right',
                    x=1
                )
            )

            # Display the bar chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    
    df_eoq = predictions_df.groupby(['ParentName','Color Code'])['Sales Predictions'].sum().reset_index()
    df_eoq['Annual Demand'] = df_eoq['Sales Predictions']*4
    df_eoq = df_eoq[df_eoq['Sales Predictions']>=1]
    # df_eoq['Kebutuhan kain (in roll)'] = (df_eoq['Sales Predictions'])*
    # df_eoq['ordering cost'] = 
    def fill_new_column(row):
        if row['ParentName'] in ['ZARIA CASUAL', 'ZARIA SAHARA']:
            return row['Sales Predictions'] * 4*1/45
        elif row['ParentName'] in ['ZARIA KIRANA', 'ZARIA CITRA']:
            return row['Sales Predictions'] *4* 1.5/45
        else:
            return row['Sales Predictions']

        # Apply the function to create a new column
    df_eoq['Kebutuhan Kain (roll)'] = df_eoq.apply(fill_new_column, axis=1)
    print(df_eoq)
    ordering_cost = 1000000
    holding_cost = 0.15*1500000

    df_eoq_new = df_eoq.groupby(['Color Code'])['Kebutuhan Kain (roll)'].sum().reset_index()
    print(df_eoq_new)

    def calculate_eoq(row):
        D = row['Kebutuhan Kain (roll)']
        S = ordering_cost
        H = holding_cost
        return np.sqrt((2 * D * S) / H)
    df_eoq_new['EOQ'] = df_eoq_new.apply(calculate_eoq, axis=1)
   
    df = df.loc[df['Color Code'] != 'UAL']
    sales_2024 = df[df['Year'] == 2024]
    stdev = sales_2024.groupby(['Color Code'])['Sales'].std().reset_index()
    stdev.columns = ['Color Code', 'Sales Std Dev']  # Rename the column for clarity

    df_eoq_new['Color Code'] = df_eoq_new['Color Code'].astype(int)
    stdev['Color Code'] = stdev['Color Code'].astype(int)

    df_eoq_new = pd.concat([df_eoq_new.set_index('Color Code'), stdev.set_index('Color Code')], axis=1, join='outer').reset_index()

    service_level = 1.65  # for 95% service level
    lead_time = 2  # in months
    def calculate_safety_stock(row):
        std_dev_demand = row['Sales Std Dev'] if pd.notna(row['Sales Std Dev']) else 0
        
        L = lead_time
        sigma_L = std_dev_demand / 45  # Monthly standard deviation
        Z = service_level
        return Z * sigma_L * np.sqrt(L)

    df_eoq_new['Safety Stock'] = df_eoq_new.apply(calculate_safety_stock, axis=1)
    #ROP
    df_eoq_new['Reorder Point'] = df_eoq_new['Safety Stock'] + (lead_time*df_eoq_new['Kebutuhan Kain (roll)']/12)

    df_eoq_new.fillna(0, inplace=True)

    df_eoq_new['Kebutuhan Kain (roll)'] = df_eoq_new['Kebutuhan Kain (roll)'].round(0).astype(int)
    df_eoq_new['EOQ'] = df_eoq_new['EOQ'].round(0).astype(int)
    df_eoq_new['Safety Stock'] = df_eoq_new['Safety Stock'].round(0).astype(int)
    df_eoq_new['Reorder Point'] = df_eoq_new['Reorder Point'].round(0).astype(int)


    st.dataframe(df_eoq_new[['Color Code', 'Kebutuhan Kain (roll)', 'EOQ', 'Safety Stock', 'Reorder Point']])


    # st.markdown(f"""
    #         <style>
    #         .card5 {{
    #             background-color: #DC3545;
    #             border-radius: 10px;
    #             padding: 20px;
    #             text-align: center;
    #             font-family: Arial, sans-serif;
    #             box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
    #             height: {fixed_height}px;
    #             display: flex;
    #             flex-direction: column;
    #             justify-content: center;
    #             margin: 10px;
    #         }}
    #         .total-RM {{
    #             font-size: 18px;
    #             font-weight: bold;
    #         }}
    #         .percentage {{
    #             font-size: 10px;
    #             font-weight: bold;
    #             color: white;
    #         }}
    #         </style>
    #         <div class="card5">
    #             <div class="total-RM">Total Raw Material Needed: {sum_kain}</div>
    #         </div>
    #     """, unsafe_allow_html=True)


    # df_mrp = predictions_df.pivot_table(index='Color Code', columns='Month', values='Sales Predictions').reset_index().round(0)
    df_mrp = predictions_df.groupby(['Color Code', 'Month'])['Sales Predictions'].sum().reset_index()
   
    df_mrp = df_mrp.pivot_table(index='Color Code', columns='Month', values='Sales Predictions')

  
    st.dataframe(df_mrp)




        
