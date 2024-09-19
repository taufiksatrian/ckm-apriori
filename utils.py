import re
import pandas as pd
import networkx as nx
import plotly.express as px
from pyvis.network import Network
from mlxtend.frequent_patterns import association_rules, apriori


def preprocess_data(df):
    df['orderTime'] = pd.to_datetime(df['orderTime'], format='%Y-%m-%d %H:%M')
    df['categoryName'] = df['categoryName'].str.lower()
    df['itemName'] = df['itemName'].str.lower()
    df['itemName'] = df['itemName'].str.strip()
    df['itemName'] = df['itemName'].apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', x))
    df['itemName'] = df['itemName'].str.replace(r'\s+', ' ', regex=True)
    invalid_items_mask = df['itemName'].str.match(r'^[^\w]+$')
    df = df[~invalid_items_mask]

    df['orderId'] = df['orderId'].astype('Int64')
    df['qty'] = df['qty'].astype('Int64')
    df['orderTime'] = pd.to_datetime(df['orderTime'])
    df = df[df['cancelReason'].isna()]
    df = df.drop(columns=['cancelReason'])

    df['qty'] = df.groupby(['orderId', 'categoryName', 'itemName'])['qty'].transform('sum')
    df = df.drop_duplicates(subset=['orderId', 'categoryName', 'itemName'])

    df['totalPrice'] = df['price'] * df['qty']
    df = df[['orderId', 'categoryName', 'itemName', 'price', 'qty', 'totalPrice', 'orderTime']]

    df['hour_in_day'] = df['orderTime'].dt.hour
    df = df[(df['hour_in_day'] >= 9) & (df['hour_in_day'] <= 21)]
    df = df.drop(columns=['hour_in_day'])

    return df


def create_basket_sets(df):
    transactions_str = df.groupby(['orderId', 'itemName'])['itemName'].count().reset_index(name='Count')
    my_basket = transactions_str.pivot_table(index='orderId', columns='itemName', values='Count', aggfunc='sum').fillna(0)
    my_basket = my_basket.astype('int64')

    def encode(x):
        if x <= 0:
            return 0
        if x >= 1:
            return 1

    my_basket_sets = my_basket.applymap(encode)
    return my_basket_sets


def calculate_apriori(df, support=0.015, min_confidence=0.25, metric="lift", min_threshold=1):
    """
    Calculate Apriori algorithm and generate association rules.

    Parameters:
    - df: DataFrame containing preprocessed transaction data.
    - support: Minimum support threshold (default is 0.01).
    - metric: Metric for association rule evaluation (default is "lift").
    - min_threshold: Minimum threshold for the metric (default is 1).
    - min_confidence: Minimum confidence threshold for the rules (default is 0.5).

    Returns:
    - rules: DataFrame containing association rules filtered by minimum confidence.
    """
    df = df.astype(bool)
    
    # Generate frequent itemsets with apriori
    frequent_items = apriori(df, min_support=support, use_colnames=True)
    
    # Generate association rules with the specified metric and min_threshold
    rules = association_rules(frequent_items, metric=metric, min_threshold=min_threshold)
    
    # Filter rules by min_confidence
    rules = rules[rules['confidence'] >= min_confidence]
    
    # Sort by confidence for easier viewing
    rules.sort_values('confidence', ascending=False, inplace=True)
    
    return rules



def display_association_rules(rules):
    """
    Display association rules in a more readable format.

    Parameters:
    - rules: DataFrame containing association rules.
    """
    rules['antecedents'] = rules['antecedents'].apply(lambda x: ', '.join(map(str, x)))
    rules['consequents'] = rules['consequents'].apply(lambda x: ', '.join(map(str, x)))
    return rules


def product_recommendation(rules, data, item):
    """
    Generate product recommendations based on association rules.

    Parameters:
    - rules: DataFrame containing association rules.
    - data: DataFrame containing transaction data.
    - item: Product for which recommendations are generated.

    Returns:
    - recommendations: List of recommended products.
    """
    recommendations = []

    relevant_rules = rules[rules['antecedents'] == item]
    recommended_items = relevant_rules['consequents']

    for recommended_item in recommended_items:
        if recommended_item not in data.columns and recommended_item != item:
            recommendations.append(recommended_item)

    return recommendations


def promo_recommendation(rules, data, item):
    """
    Generate promotional recommendations based on association rules.

    Parameters:
    - rules: DataFrame containing association rules.
    - item: Product for which promotional recommendations are generated.

    Returns:
    - promo: List of recommended promotions.
    """
    promo = []
    relevant_rules = rules[rules['antecedents'] == item]
    
    if not relevant_rules.empty:
        # Create a DataFrame to store the recommendations
        recommended_df = relevant_rules.explode('consequents')
        recommended_df = recommended_df[recommended_df['consequents'] != item]
        recommended_df = recommended_df[~recommended_df['consequents'].isin(data.columns)]
        
        # Map the results to the desired format
        promo = recommended_df[['antecedents', 'consequents', 'confidence']].apply(
            lambda row: {'Package': f"{item} + {row['consequents']}", 'Confidence': row['confidence']},
            axis=1
        ).tolist()
    
    return promo


def plot_frequency_of_items(df):
    Frequency_of_items = df.groupby(pd.Grouper(key='itemName')).size().reset_index(name='count')
    fig = px.treemap(Frequency_of_items, path=['itemName'], values='count')
    fig.update_layout(title_text='Frequency of the Items Sold')
    fig.update_traces(textinfo="label+value")
    return fig

def plot_top_items(df):
    top_items = df['itemName'].value_counts().head(20).sort_values(ascending=True)
    fig = px.bar(y=top_items.index, x=top_items.values,  # Swap x and y
                labels={'y': 'Items', 'x': 'Count of Items'},
                title='Top 20 Items purchased by customers', 
                width=1000, height=500, orientation='h')  # Set orientation to horizontal
    
    for trace in fig.data:
        for i, value in enumerate(trace.x):  # Now use x values for annotations
            fig.add_annotation(
                y=trace.y[i],
                x=value,
                text=f'{value}',  
                showarrow=False,
                arrowhead=4,
                ax=-30,
                ay=0,
                xshift=20
            )
    return fig


def plot_least_sold_items(df):
    """
    Plot the Top 20 Least Sold Items.
    
    Parameters:
    - df: DataFrame containing transaction data.
    
    Returns:
    - fig: A Plotly bar chart figure.
    """
    least_sold_items = df['itemName'].value_counts().tail(20).sort_values(ascending=False)  # Sort in ascending order for y-axis
    fig = px.bar(y=least_sold_items.index, x=least_sold_items.values,  # Swap x and y
                labels={'y': 'Items', 'x': 'Count of Items'},
                title='Top 20 Least Sold Items', 
                width=1000, height=500, orientation='h')  # Set orientation to horizontal
    
    for trace in fig.data:
        for i, value in enumerate(trace.x):  # Use x values for annotations (counts)
            fig.add_annotation(
                y=trace.y[i],
                x=value,
                text=f'{value}',  
                showarrow=False,
                arrowhead=4,
                ax=-30,
                ay=0,
                xshift=10
            )
    
    return fig

def plot_total_transactions(df, time_period='D'):
    """
    Plots the total transactions based on the specified time period in a line chart.

    Parameters:
    - df: DataFrame containing the transaction data.
    - time_period: A string specifying the time period for aggregation.
        Options include:
        'D' for daily, 
        'W' for weekly, 
        'M' for monthly, 
        'Y' for yearly.

    Returns:
    - fig: A Plotly line chart figure showing total transactions per time period.
    """
    # Group the data by the specified time period and count unique transactions
    total_transactions = df.groupby(df['orderTime'].dt.to_period(time_period))['orderId'].nunique().reset_index()

    # Format the time period for better readability in the chart
    total_transactions['orderTime'] = total_transactions['orderTime'].astype(str)

    # Create the line plot using Plotly Express
    fig = px.line(total_transactions, x='orderTime', y='orderId',
                title=f'Total Transactions Over Time ({time_period})',
                labels={'orderTime': 'Time Period', 'orderId': 'Total Transactions'},
                markers=True)

    fig.update_layout(xaxis_title='Time Period', yaxis_title='Total Transactions')

    # Add annotations for each point in the line chart
    for trace in fig.data:
        for i, value in enumerate(trace.y):
            fig.add_annotation(
                x=trace.x[i],
                y=value,
                text=f'{value}',  
                showarrow=False,
                arrowhead=4,
                ax=0,
                ay=-20,
                yshift=10
            )

    return fig

def plot_monthly_total_price(df):
    monthly_total_price = df.groupby(df['orderTime'].dt.to_period("M"))['totalPrice'].sum().reset_index()
    monthly_total_price['orderTime'] = monthly_total_price['orderTime'].dt.strftime('%Y-%m')
    month_names = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    monthly_total_price['orderTime'] = monthly_total_price['orderTime'].apply(lambda x: month_names[x.split('-')[1]])
    
    fig = px.bar(monthly_total_price, x='orderTime', y='totalPrice',
                title='Total Omzet DKriuk every Month in 2023',
                labels={'orderTime': 'Month', 'totalPrice': 'Total Omzet'})
    fig.update_layout(xaxis=dict(type='category'), xaxis_title='Month', yaxis_title='Total Omzet')
    
    for trace in fig.data:
        for i, value in enumerate(trace.y):
            value_in_millions = value / 1000000
            fig.add_annotation(
                x=trace.x[i],
                y=value,
                text=f'{value_in_millions:.2f} Juta',  
                showarrow=False,
                arrowhead=4,
                ax=0,
                ay=-30,
                yshift=10 
            )
    return fig

def plot_monthly_total_transaction(df):
    monthly_total_transaction = df.groupby(df['orderTime'].dt.to_period("M"))['orderId'].nunique().reset_index()
    monthly_total_transaction['orderTime'] = monthly_total_transaction['orderTime'].dt.strftime('%Y-%m')
    month_names = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
                '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    monthly_total_transaction['orderTime'] = monthly_total_transaction['orderTime'].apply(lambda x: month_names[x.split('-')[1]])
    
    fig = px.bar(monthly_total_transaction, x='orderTime', y='orderId',
                title='Total Transaction every Month in 2023',
                labels={'orderTime': 'Month', 'orderId': 'Total Transaction'})
    fig.update_layout(xaxis=dict(type='category'), xaxis_title='Month', yaxis_title='Total Transaction')
    
    for trace in fig.data:
        for i, value in enumerate(trace.y):
            fig.add_annotation(
                x=trace.x[i],
                y=value,
                text=f'{value}',  
                showarrow=False,
                arrowhead=4,
                ax=0,
                ay=-30,
                yshift=10 
            )
    return fig

def plot_weekly_total_transaction(df):
    df['week_number'] = df['orderTime'].dt.isocalendar().week
    weekly_total_transaction = df.groupby((df['week_number'] - 1) % 4)['orderId'].nunique().reset_index()
    weekly_total_transaction['week_number'] = weekly_total_transaction['week_number'].map({0: 1, 1: 2, 2: 3, 3: 4})
    
    fig = px.bar(weekly_total_transaction, x='week_number', y='orderId', 
                title='Total Transactions every Week in 2023',
                labels={'week_number': 'Week', 'orderId': 'Total Transactions'})
    fig.update_xaxes(tickvals=[1, 2, 3, 4])
    
    for trace in fig.data:
        for i, value in enumerate(trace.y):
            fig.add_annotation(
                x=trace.x[i],
                y=value,
                text=f'{value}',  
                showarrow=False,
                arrowhead=4,
                ax=0,
                ay=-30,
                yshift=10 
            )
    return fig

def plot_daily_total_transaction(df):
    df['day_of_week'] = df['orderTime'].dt.day_name()
    weekly_total_transaction = df.groupby('day_of_week')['orderId'].nunique().reset_index()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_total_transaction['day_of_week'] = pd.Categorical(weekly_total_transaction['day_of_week'], categories=days_order, ordered=True)
    weekly_total_transaction = weekly_total_transaction.sort_values('day_of_week')
    
    fig = px.bar(weekly_total_transaction, x='day_of_week', y='orderId', 
                title='Total Transactions every Day of the Week in 2023',
                labels={'day_of_week': 'Day', 'orderId': 'Total Transactions'})
    
    for trace in fig.data:
        for i, value in enumerate(trace.y):
            fig.add_annotation(
                x=trace.x[i],
                y=value,
                text=f'{value}',  
                showarrow=False,
                arrowhead=4,
                ax=0,
                ay=-30,
                yshift=10 
            )
    return fig

def plot_hourly_total_transaction(df):
    df['hour_of_day'] = df['orderTime'].dt.hour
    hourly_total_transaction = df.groupby('hour_of_day')['orderId'].nunique().reset_index()
    
    fig = px.bar(hourly_total_transaction, x='hour_of_day', y='orderId', 
                title='Total Transactions every Hour of the Day in 2023',
                labels={'hour_of_day': 'Hour', 'orderId': 'Total Transactions'},
                category_orders={'hour_of_day': list(range(1, 25))})
    
    fig.update_layout(
        xaxis=dict(
            tickvals=list(range(1, 25)),
            ticktext=[str(i) for i in range(1, 25)]
        )
    )
    
    for trace in fig.data:
        for i, value in enumerate(trace.y):
            fig.add_annotation(
                x=trace.x[i],
                y=value,
                text=f'{value}',  
                showarrow=False,
                arrowhead=4,
                ax=0,
                ay=-30,
                yshift=10 
            )
    return fig


def generate_pyvis_graph(rules):
    """
    Generate a Pyvis graph from the association rules DataFrame and return the HTML representation.
    """
    graph = rules[['antecedents', 'consequents', 'confidence', 'antecedent support', 'consequent support']]
    
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    for index, row in graph.iterrows():
        antecedents = ", ".join(list(row['antecedents'])) if isinstance(row['antecedents'], frozenset) else row['antecedents']
        consequents = ", ".join(list(row['consequents'])) if isinstance(row['consequents'], frozenset) else row['consequents']
        weight = round(row['confidence'], 2)
        ant_support = row['antecedent support']
        con_support = row['consequent support']

        G.add_node(antecedents, size=ant_support * 100, title=f"Support: {ant_support}")
        G.add_node(consequents, size=con_support * 100, title=f"Support: {con_support}")
        G.add_edge(antecedents, consequents, weight=weight, title=f"Confidence: {weight}")

    # Normalize edge sizes
    max_confidence = max(graph['confidence'])
    min_confidence = min(graph['confidence'])

    # Avoid division by zero
    if max_confidence == min_confidence:
        for u, v, d in G.edges(data=True):
            G[u][v]['value'] = 1 
    else:
        for u, v, d in G.edges(data=True):
            weight = d['weight']
            value = 1 + 9 * (weight - min_confidence) / (max_confidence - min_confidence)
            G[u][v]['value'] = value

    # Create a Pyvis Network
    net = Network(notebook=True, directed=True, cdn_resources='in_line')

    # Load the NetworkX graph into Pyvis Network
    net.from_nx(G)

    # Customize the layout and appearance
    net.set_options("""
    var options = {
        "nodes": {
            "scaling": {
                "min": 10,
                "max": 50
            }
        },
        "edges": {
            "scaling": {
                "label": {
                    "enabled": true
                }
            },
            "smooth": true
        },
        "interaction": {
            "hover": true
        },
        "physics": {
            "enabled": true
        }
    }
    """)

    # Return the HTML of the network
    return net.generate_html()

def plot_top_association_rules(rules, metric='confidence', top_n=10):
    """
    Generate a bar chart for the top association rules based on the specified metric.

    Parameters:
    - rules: DataFrame containing association rules with metrics (confidence, lift, support).
    - metric: The metric to rank the rules by. Options: 'confidence', 'lift', 'support'.
    - top_n: The number of top rules to display in the chart.

    Returns:
    - fig: Plotly bar chart figure.
    """
    # Sort the rules by the selected metric in descending order and select the top N rules
    top_rules = rules.nlargest(top_n, metric)
    
    # Create labels for each rule by combining antecedents and consequents
    top_rules['rule'] = top_rules.apply(lambda row: f"{', '.join(list(row['antecedents'])) if isinstance(row['antecedents'], frozenset) else row['antecedents']} -> {', '.join(list(row['consequents'])) if isinstance(row['consequents'], frozenset) else row['consequents']}", axis=1)
    top_rules = top_rules.sort_values(by=metric, ascending=True)

    # Create the bar chart
    fig = px.bar(top_rules, 
                x=metric, 
                y='rule', 
                height=600, orientation='h',  # Set orientation to horizontal
                title=f'Top {top_n} Association Rules by {metric.capitalize()}',
                labels={'rule': 'Association Rule', metric: metric.capitalize()},
                text=metric)
    
    # Customize the layout for better readability
    fig.update_layout(
        xaxis_title=metric.capitalize(),
        yaxis_title='Association Rule'
    )
    
    # Add text annotations to each bar
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    return fig