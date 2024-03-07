import numpy as np
import holoviews as hv
import streamlit as st
import altair as alt
import panel as pn
import pandas as pd


# 定义页面功能
def page1():
    # 确保 'insurance.csv' 文件在当前目录中
    df = pd.read_csv('../insurance.csv')
    # 初始化session state变量
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

    # 设置页面标题
    st.title('Insurance Data  Dashboard')


    st.markdown(intro_text)
    # 添加交互组件以筛选数据
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

    # 根据用户输入筛选数据
    filtered_df = df[(df['age'].between(*age)) & 
                    (df['sex'].isin(sex)) & 
                    (df['bmi'].between(*bmi)) & 
                    (df['children'].between(*children)) & 
                    (df['smoker'].isin(smoker)) & 
                    (df['region'].isin(region))]

    # 添加选择每页显示条目数的选项，并更新 session state
    entries_option = st.selectbox('Show entries:', [10, 25, 50], index=0)
    if entries_option != st.session_state.entries_per_page:
        st.session_state.entries_per_page = entries_option
        st.session_state.page_number = 1

    # 计算总页数
    total_pages = len(filtered_df) // st.session_state.entries_per_page + (len(filtered_df) % st.session_state.entries_per_page > 0)


    # 分页控制器
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


    # 计算开始和结束索引
    start_index = (st.session_state.page_number - 1) * st.session_state.entries_per_page
    end_index = start_index + st.session_state.entries_per_page

    # 显示当前页面的数据
    st.dataframe(filtered_df.iloc[start_index:end_index])

    # 显示当前页码和总页数
    st.text(f"Showing page {st.session_state.page_number} of {total_pages}")
    

def page2():
    # 加载数据
    dat = pd.read_csv('../insurance.csv')
    
    # 设置页面标题
    st.title('Interactive Analysis of Health Insurance Costs Based on BMI, Smoking Status and Demographics')

    # 创建选择器，用于鼠标悬停时选择最近的点
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['bmi'], empty='none')
    # 定义图表的共享宽度和高度
    chart_width = 600
    chart_height = 300

    # UI 控件用于筛选数据，放在页面中而不是侧边栏
    smoker_filter = st.multiselect(
        'Select Smoker Status:', options=dat['smoker'].unique(), default=dat['smoker'].unique()
    )
    sex_filter = st.multiselect(
        'Select Sex:', options=dat['sex'].unique(), default=dat['sex'].unique()
    )
    region_filter = st.multiselect(
        'Select Region:', options=dat['region'].unique(), default=dat['region'].unique()
    )

    # 根据筛选器更新数据
    filtered_data = dat[
        dat['smoker'].isin(smoker_filter) & 
        dat['sex'].isin(sex_filter) & 
        dat['region'].isin(region_filter)
    ]
    # Step 1: Create an interval selection for both charts to use
    interval = alt.selection_interval(encodings=['x'])
    
    # 基本线图，并设置颜色
    line = alt.Chart(filtered_data).mark_line(interpolate='basis', color='orange').encode(
        x='bmi',
        y='charges',
        color=alt.value('#c0a9bd')  # 设置为橙色
    )
    # 透明选择器图表
    selectors = alt.Chart(filtered_data).mark_point().encode(
        x='bmi',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # 线图上的点，基于选择器高亮
    points = line.mark_point(color='#6c757d').encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
        color=alt.value('#a4d8d6')  # 浅绿色
    )

    # 线图上的文本标签，基于选择器高亮
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'charges', alt.value(' ')),
        color=alt.value('#ffbb98')  # 橙色
    )

    # 根据选择器位置绘制规则线
    rules = alt.Chart(filtered_data).mark_rule(color='gray').encode(
        x='bmi',
    ).transform_filter(nearest)

    # 组合所有图层成为线图，并设置宽度和高度
    line_chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=chart_width, 
        height=chart_height,
        title='BMI vs. Charges by Smoker Status'
    )

    # 交互式散点图，根据年龄来调整大小
    scatter_plot = alt.Chart(filtered_data).mark_point().encode(
        x=alt.X('bmi', scale=alt.Scale(zero=False)),
        y=alt.Y('charges', scale=alt.Scale(zero=False)),
        color=alt.Color('smoker:N', legend=alt.Legend(title='Smoker'),
                        scale=alt.Scale(domain=['no', 'yes'], range=['navy', 'orange'])),
    size=alt.Size('age:Q', bin=alt.Bin(maxbins=3), legend=alt.Legend(title='Age')),  # 使用 maxbins 参数减少年龄区间数量
        tooltip=['bmi', 'charges', 'smoker', 'age']
    ).properties(
        width=chart_width, 
        height=chart_height,
        title='Scatter Plot of Charges vs. BMI'
    ).interactive()

    # 使用 & 操作符垂直连接图表
    combined_chart = (line_chart & scatter_plot).resolve_scale(color='independent')

    # 在 Streamlit 中显示图表
    st.altair_chart(combined_chart, use_container_width=True)
    st.write("This is page 2.")





def page3():
    # page3 相关的代码
    # 加载数据
# 加载数据
    dat = pd.read_csv('../insurance.csv')

    # 创建选择器，用于在图表上选择间隔
    interval = alt.selection_interval()

    # 定义图表的共享宽度和高度
    chart_width = 600
    chart_height = 300

    # UI 控件用于筛选数据，放在页面中而不是侧边栏
    smoker_filter = st.multiselect(
        'Select Smoker Status:', options=dat['smoker'].unique(), default=dat['smoker'].unique()
    )
    sex_filter = st.multiselect(
        'Select Sex:', options=dat['sex'].unique(), default=dat['sex'].unique()
    )
    region_filter = st.multiselect(
        'Select Region:', options=dat['region'].unique(), default=dat['region'].unique()
    )

    # 根据筛选器更新数据
    filtered_data = dat[
        dat['smoker'].isin(smoker_filter) & 
        dat['sex'].isin(sex_filter) & 
        dat['region'].isin(region_filter)
    ]

    # 组合所有图层成为线图，并设置颜色，添加选择器
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

    # 交互式散点图，根据年龄来调整大小，添加选择器
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

    # 使用 & 操作符垂直连接图表
    combined_chart = alt.vconcat(line_chart, scatter_plot).resolve_scale(color='independent')

    # 在 Streamlit 中显示图表
    st.altair_chart(combined_chart, use_container_width=True)
    st.write("This is page 3.")





def page4():
    # 加载数据
    data = pd.read_csv('../insurance.csv')
    # 定义一个下拉选择器，用于地区筛选
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
    # 更新散点图，包括地区筛选功能
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
    # 创建组合图表时，确保颜色比例和图例是独立的
    combined_chart = alt.vconcat(
        (bar_chart | scatter_plot_with_filters).resolve_scale(color='independent')
    ).resolve_legend(
        color='independent',
        shape='independent'
    )

    st.altair_chart(combined_chart.interactive(), use_container_width=True)


    st.write("This is page 4.")



def page5():
    # 加载数据
    data = pd.read_csv('../insurance.csv')

    # 创建一个间隔选择器
    interval = alt.selection_interval()

    # 定义一个基本的散点图，设置透明度和颜色条件
    base = alt.Chart(data).mark_circle().encode(
        opacity=alt.condition(interval, alt.value(1), alt.value(0.2)),
        color=alt.condition(interval, 'region:N', alt.value('lightgray'))
    ).properties(
        width=300,
        height=300
    ).add_selection(
        interval
    )

    # 左图：按年龄划分的费用
    charges_age_chart = base.encode(
        x='age:Q',
        y='charges:Q',
        tooltip=['age', 'charges', 'region']
    )

    # 右图：BMI与子女数量的关系
    children_bmi_chart = base.encode(
        x='bmi:Q',
        y='children:Q',
        tooltip=['bmi', 'children', 'region']
    )

    # 水平排列图表
    combined_charts = alt.hconcat(charges_age_chart, children_bmi_chart)

    # 使用 Streamlit 显示图表
    st.altair_chart(combined_charts, use_container_width=True)

    st.write("This is page 5.")
















# 侧边栏选项
st.sidebar.title('Navigation')
options = ["General Information", "Charges Comparison", "Charges Selection", "Region Insights",'Age Difference']
choice = st.sidebar.radio("Choose a page:", options)

# 在这里添加组名和小组成员信息
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('') 
st.sidebar.markdown('---') # 添加一条分割线

st.sidebar.markdown('### Team VisPro')
st.sidebar.markdown("""
- Zheng Wan
- Weijing Zeng
- Nhu Pham
""")

# 根据侧边栏的选择显示对应的页面内容
if choice == "General Information":
    page1()
elif choice == "Charges Comparison":
    page2()
elif choice == "Charges Selection":
    page3()
elif choice == "Region Insights":
    page4()
elif choice == "Age Difference":
    page5()



