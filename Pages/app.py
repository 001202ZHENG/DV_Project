import numpy as np
import holoviews as hv
import streamlit as st
import altair as alt
import panel as pn
import pandas as pd




# Define page functionality
def page1():
    df = pd.read_csv('../insurance.csv')
    # Initialize session state variables
    if 'page_number' not in st.session_state:
        st.session_state['page_number'] = 1
    if 'entries_per_page' not in st.session_state:
        st.session_state['entries_per_page'] = 10

    # Introduction text
    intro_text = """
    ## Introduction

    This dashboard is our  Interactive Data Storytelling for the data visualization course.Users can experience different types of components by selecting options in the left sidebar.

    ### Description:
    Healthcare insurance cost analysis is a significant area of interest as it provides insights into factors influencing insurance premiums, helps in understanding the financial burden on individuals, and aids in policy-making decisions for healthcare systems. 

    The dataset chosen for this analysis contains information about individuals' attributes and their corresponding healthcare insurance charges.

    This dataset has 6 variable:

    1. Age: age of primary beneficiary.

    2. Sex: insurance contractor gender, female, male.

    3. BMI: an objective index of body weight relative to height
    4. Children: Number of children covered by health insurance/Number of dependents.

    5. Smoker: Is the person a smoker or not.

    6. Region: the beneficiary's residential area in the US, northeast, southeast, southwest, northwest.

    7. Charges: Individual medical costs billed by health insurance.
        
    Below, you can interactively filter and explore the data:

    ### Filter & Visualization:
    """

    # Set the page title
    st.title('Insurance Data  Dashboard')


    st.markdown(intro_text)
    # Add interactive components to filter data
    age = st.slider('Age', min_value=int(df['age'].min()), max_value=int(df['age'].max()), value=(int(df['age'].min()), int(df['age'].max())))
    bmi = st.slider('BMI', min_value=float(df['bmi'].min()), max_value=float(df['bmi'].max()), value=(float(df['bmi'].min()), float(df['bmi'].max())))
    children = st.slider('Children', min_value=int(df['children'].min()), max_value=int(df['children'].max()), value=(int(df['children'].min()), int(df['children'].max())))

    region = st.multiselect('Region', options=df['region'].unique(), default=df['region'].unique())
    sex = st.multiselect('Sex', options=df['sex'].unique(), default=df['sex'].unique())
    smoker = st.multiselect('Smoker', options=df['smoker'].unique(), default=df['smoker'].unique())


    # Create a selectbox for user to choose the column to sort by
    sort_by = st.selectbox('Sort by', ['age', 'sex', 'bmi', 'children', 'smoker', 'region', 'charges'])
    # Create a checkbox for user to choose sorting order
    sort_order = st.checkbox('Ascending', True)

    # Sort the dataframe by selected column and order
    if sort_order:
        df = df.sort_values(by=sort_by, ascending=True)
    else:
        df = df.sort_values(by=sort_by, ascending=False)

    # Filter data based on user input
    filtered_df = df[(df['age'].between(*age)) & 
                    (df['sex'].isin(sex)) & 
                    (df['bmi'].between(*bmi)) & 
                    (df['children'].between(*children)) & 
                    (df['smoker'].isin(smoker)) & 
                    (df['region'].isin(region))]

    # Add a selection option for the number of entries per page and update the session state
    entries_option = st.selectbox('Show entries:', [10, 25, 50], index=0)
    if entries_option != st.session_state.entries_per_page:
        st.session_state.entries_per_page = entries_option
        st.session_state.page_number = 1

    # Calculate total number of pages
    total_pages = len(filtered_df) // st.session_state.entries_per_page + (len(filtered_df) % st.session_state.entries_per_page > 0)


    # Pagination controls
    prev, _ ,next = st.columns([1, 1, 1])

    with prev:
        if st.button('Previous'):
            if st.session_state.page_number > 1:
                st.session_state.page_number -= 1
            st.experimental_rerun()

    with next:
        if st.button('Next'):
            if st.session_state.page_number < total_pages:
                st.session_state.page_number += 1
            st.experimental_rerun()


    # Calculate start and end index
    start_index = (st.session_state.page_number - 1) * st.session_state.entries_per_page
    end_index = start_index + st.session_state.entries_per_page

    # Display the data for the current page
    st.dataframe(filtered_df.iloc[start_index:end_index])

    # Display the current page number and total pages
    st.text(f"Showing page {st.session_state.page_number} of {total_pages}")
    


def page2():
    # Load data
    dat = pd.read_csv('../insurance.csv')

    # Create selector for selecting intervals on charts
    interval = alt.selection_interval()

    # Define shared width and height for charts
    chart_width = 600
    chart_height = 300

    # UI controls for filtering data, placed on the page instead of the sidebar
    smoker_filter = st.multiselect(
        'Select Smoker Status:', options=dat['smoker'].unique(), default=dat['smoker'].unique()
    )
    sex_filter = st.multiselect(
        'Select Sex:', options=dat['sex'].unique(), default=dat['sex'].unique()
    )
    region_filter = st.multiselect(
        'Select Region:', options=dat['region'].unique(), default=dat['region'].unique()
    )

    # Update data based on filters
    filtered_data = dat[
        dat['smoker'].isin(smoker_filter) & 
        dat['sex'].isin(sex_filter) & 
        dat['region'].isin(region_filter)
    ]

    # Combine all layers into line chart, set color, and add selector
    line_chart = alt.Chart(filtered_data).mark_line(interpolate='basis').encode(
        x='bmi',
        y='charges',
        color='smoker:N'
    ).properties(
        width=chart_width, 
        height=chart_height,
        title='BMI vs. Charges by Smoker Status'
    ).add_selection(
        interval  # Add our interval selection to the chart
    )

    # Interactive scatter plot, adjusting size based on age, and add selector
    scatter_plot = alt.Chart(filtered_data).mark_point().encode(
        x='bmi',
        y='charges',
        color=alt.condition(interval, 'smoker:N', alt.value('lightgray')),  # Change color based on selection
        size='age:Q'
    ).properties(
        width=chart_width, 
        height=chart_height,
        title='Scatter Plot of Charges vs. BMI'
    ).add_selection(
        interval  # Use the same selection for this chart
    ).interactive()

    # Vertically concatenate charts using & operator
    combined_chart = alt.vconcat(line_chart, scatter_plot).resolve_scale(color='independent')

    # Display charts in Streamlit
    st.altair_chart(combined_chart, use_container_width=True)
    st.write("This is page 2.")
    st.write("The graphs illustrate the relationship between Body Mass Index (BMI) and healthcare charges, differentiated by smoking status. It clearly indicates that smokers, across all BMIs, typically incur higher healthcare costs than their non-smoking counterparts. Notably, for individuals with a BMI over 30, the charges for smokers can be up to two to three times higher than for non-smokers with an equivalent BMI. Beyond a BMI of 40, the trend shows that charges for non-smokers tend to decrease, whereas costs for smokers display some variability.")

def page3():
    # Load data
    data = pd.read_csv('../insurance.csv')
    # Define a dropdown selector for region filtering
    region_selection = alt.selection_single(name='RegionSelection', fields=['region'], bind='legend')

    # Average charges by region - Bar Chart
    bar_chart = alt.Chart(data).mark_bar().encode(
        x='region:N',
        y='average(charges):Q',
        color=alt.condition(region_selection, 'region:N', alt.value('lightgray')),
        tooltip=['region:N', 'average(charges):Q']
    ).add_selection(
        region_selection
    )

    region_dropdown = alt.binding_select(options=[None] + sorted(data['region'].unique()), name='Region Filter: ')
    region_selection2 = alt.selection_single(fields=['region'], bind=region_dropdown, empty='all')

    smoker_selection = alt.selection_single(name='SmokerSelection', fields=['smoker'], bind='legend')
    # Update scatter plot, including region filtering functionality
    scatter_plot_with_filters = alt.Chart(data).mark_point().encode(
        x='age:Q',
        y='charges:Q',
        color='smoker:N',
        tooltip=['age:Q', 'charges:Q', 'smoker:N', 'region:N'],
        opacity=alt.condition(smoker_selection & region_selection2, alt.value(1), alt.value(0.2))
    ).add_selection(
        smoker_selection,
        region_selection2
    )
    # When creating combined charts, ensure color scale and legend are independent
    combined_chart = alt.vconcat(
        (bar_chart | scatter_plot_with_filters).resolve_scale(color='independent')
    ).resolve_legend(
        color='independent',
        shape='independent'
    )

    st.altair_chart(combined_chart.interactive(), use_container_width=True)


    st.write("This is page 3.")
    st.write("The analysis of medical charges across all regions reveals a consistent range of 12000 to 15000, with the Southeast region standing out for its highest average charges. Moreover, examining age versus charges illustrates a predictable trend: as age increases, so do medical expenses. This relationship is further underscored by a significant divergence between smokers and non-smokers, with smokers facing markedly higher charges, often 4 to 5 times that of non-smokers. Intriguingly, the minimum charges for smokers can match or surpass the highest charges among non-smokers. Notably, in the Southeast region, these higher charges are predominantly attributed to smokers, contributing to its status of having the highest average charges among all regions.")

def page4():
    # Load data
    data = pd.read_csv('../insurance.csv')

    # Create an interval selector
    interval = alt.selection_interval()

    # Define a basic scatter plot, setting opacity and color conditions
    base = alt.Chart(data).mark_circle().encode(
        opacity=alt.condition(interval, alt.value(1), alt.value(0.2)),
        color=alt.condition(interval, 'region:N', alt.value('lightgray'))
    ).properties(
        width=300,
        height=300
    ).add_selection(
        interval
    )

    # Left chart: Charges divided by age
    charges_age_chart = base.encode(
        x='age:Q',
        y='charges:Q',
        tooltip=['age', 'charges', 'region']
    )

    # Right chart: Relationship between BMI and number of children
    children_bmi_chart = base.encode(
        x='bmi:Q',
        y='children:Q',
        tooltip=['bmi', 'children', 'region']
    )

    # Horizontally arrange charts
    combined_charts = alt.hconcat(charges_age_chart, children_bmi_chart)

    # Display charts using Streamlit
    st.altair_chart(combined_charts, use_container_width=True)

    st.write("This is page 4.")
    st.write("Notably, healthcare charges are relatively low for the younger population but begin to rise more steeply past a certain age, suggesting higher medical costs as people grow older. Conversely, when examining the number of children in relation to Body Mass Index (BMI), there is no discernible trend, which suggests that the number of children is independent of BMI and is uniformly distributed across the different regions.")

# Sidebar options
st.sidebar.title('Navigation')
options = ["General Information", "Charges Selection", "Region Insights", 'Age Difference']
choice = st.sidebar.radio("Choose a page:", options)

# Add group name and team members' information here
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('---') # Add a horizontal line

st.sidebar.markdown('### Team VisPro')
st.sidebar.markdown("""
- Zheng Wan
- Weijing Zeng
- Nhu Pham
""")

# Display corresponding page content based on sidebar selection
if choice == "General Information":
    page1()
elif choice == "Charges Selection":
    page2()
elif choice == "Region Insights":
    page3()
elif choice == "Age Difference":
    page4()
