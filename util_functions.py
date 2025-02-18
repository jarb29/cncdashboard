import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from decimal import Decimal
import numpy as np
import base64
from io import BytesIO


def get_months_and_years_since(date_str):
    initial_date = datetime.strptime(date_str, "%d/%m/%Y")
    current_date = datetime.now()

    months = set()
    years = set()

    while initial_date <= current_date:
        months.add(initial_date.month)
        years.add(initial_date.year)
        initial_date = add_months(initial_date, 1)

    # Separate current month and year
    cur_month = current_date.month
    cur_year = current_date.year

    return sorted(list(months)), sorted(list(years)), cur_month, cur_year


def add_months(date, months):
    month = date.month - 1 + months
    year = date.year + month // 12
    month = month % 12 + 1
    day = min(date.day, [31,29,31,30,31,30,31,31,30,31,30,31][month-1])
    return datetime(year, month, day)




def filter_by_year_month(df, year, month, nego):
    filtered_items = []
    for index, row in df.iterrows():
        close_at_date = row['Terminado']
        if pd.to_datetime(close_at_date).year == year and pd.to_datetime(close_at_date).month == month and row['negocio']== nego:
            filtered_items.append(row)
    return pd.DataFrame(filtered_items)

def filter_by_year_month_only(df, year, month):
    """
    Filters a DataFrame to include only rows where the 'Terminado' column matches
    the specified year and month.

    :param df: The input DataFrame.
    :param year: The year to filter by.
    :param month: The month to filter by.
    :return: A DataFrame filtered by the specified year and month.
    """
    # Ensure 'Terminado' is in datetime format
    filtered_items = []
    for index, row in df.iterrows():
        close_at_date = row['Terminado']
        if pd.to_datetime(close_at_date).year == year and pd.to_datetime(close_at_date).month == month:
            filtered_items.append(row)
    return pd.DataFrame(filtered_items)




def create_dataframe_from_items(items):
    columns = [
        'pv', 'Inicio', 'cantidadPerforacionesTotal', 'Terminado', 'cantidadPerforacionesPlacas', 'kg',
        'tipoMecanizado', 'progress_createdAt', 'origen', 'maquina', 'placas', 'hora_reporte', 'tiempo',
        'tiempo_seteo', 'espesor', 'negocio', 'cliente', 'posicion'
    ]

    rows = []

    for item in items:
        # Extract the fixed part of the data with renamed columns
        fixed_values = {
            'pv': item['pv'],
            'Inicio': item['data']['createdAt'],
            'cantidadPerforacionesTotal': item['data']['cantidadPerforacionesTotal'],
            'Terminado': item['timestamp'],
            'cantidadPerforacionesPlacas': item['data']['cantidadPerforacionesPlacas'],
            'kg': item['data']['kg'],
            'tipoMecanizado': item['data']['tipoMecanizado'],
            'espesor': item['data'].get('espesor', 0),  # Assuming 'espesor' comes from 'data' dictionary
            'cliente': item['data']['cliente'],
            'posicion': item['posicion']
        }

        # Process each progress element
        for progress_item in item['data']['progress']:
            row = {
                'progress_createdAt': progress_item.get('createdAt', '0'),
                'origen': progress_item.get('origen', '0'),
                'maquina': progress_item.get('maquina', '0'),
                'placas': float(progress_item.get('placas', 0)) if 'placas' in progress_item else 0,
                'hora_reporte': progress_item.get('hora_reporte', '0'),
                'negocio': item['data'].get('negocio', 'does not exist'),
                'tiempo': float(progress_item.get('tiempo', 0)) if 'tiempo' in progress_item else 0,
                'tiempo_seteo': float(progress_item.get('tiempo_seteo', 0)) if 'tiempo_seteo' in progress_item else 0
            }

            # Combine fixed values with progress item specific values
            combined_row = {**fixed_values, **row}
            rows.append(combined_row)

    # Create DataFrame from rows
    df = pd.DataFrame(rows, columns=columns)
    df['Inicio'] = pd.to_datetime(df['Inicio'], errors='coerce')
    df['Terminado'] = pd.to_datetime(df['Terminado'], errors='coerce')
    columns_to_convert = ['placas', 'cantidadPerforacionesPlacas']
    for col in columns_to_convert:
        df[col] = df[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

    df['perforaTotal'] = df['placas']*df['cantidadPerforacionesPlacas']
    df['Tiempo Proceso (min)'] = round((df['Terminado'] - df['Inicio']).dt.total_seconds() / 60, 2)

    return df




def filter_and_drop_columns(df, filter_column, filter_value, columns_to_drop):
    """
    Filters a DataFrame by a specified value in a given column and drops specified columns.

    Parameters:
    - df (pd.DataFrame): The DataFrame to filter and drop columns from.
    - filter_column (str): The name of the column to filter by.
    - filter_value (any): The value to filter out from the DataFrame.
    - columns_to_drop (list): A list of columns to drop from the DataFrame if they exist.

    Returns:
    - pd.DataFrame: The filtered DataFrame with specified columns dropped.
    """
    filtered_df = df[df[filter_column] != filter_value]
    filtered_df = filtered_df.drop(columns=[col for col in columns_to_drop if col in filtered_df.columns])
    # Reset the index
    filtered_df = filtered_df.reset_index(drop=True)
    return filtered_df



def group_and_average(df, group_columns, avg_column):
    """
    Groups a DataFrame by specified columns and computes the average of another column.

    Parameters:
    - df (pd.DataFrame): The DataFrame to group.
    - group_columns (list): A list of column names to group by.
    - avg_column (str): The name of the column to compute the average for.

    Returns:
    - pd.DataFrame: A DataFrame with the grouped columns and the average values.
    """
    # Group the DataFrame by the specified columns and compute the mean of the avg_column
    grouped_df = df.groupby(group_columns, as_index=False)[avg_column].mean()
    grouped_df[avg_column] = grouped_df[avg_column].round(2)
    return grouped_df

precio = {'sabimet': 226, 'steelk': 108}


def calculate_price(row):
    return row['mm de perforado'] * precio.get(row['negocio'], 1)


def group_and_sum_without_remove_columns(df, group_columns, avg_column,
                                         cols_to_convert=['cantidadPerforacionesPlacas', 'kg', 'placas', 'espesor',
                                                          'perforaTotal']):
    df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='ignore')

    agg_dict = {col: 'first' for col in df.columns if col not in group_columns + [avg_column]}
    agg_dict[avg_column] = 'sum'

    grouped_df = df.groupby(group_columns, as_index=False).agg(agg_dict)
    grouped_df[avg_column] = grouped_df[avg_column].round(2)

    grouped_df = grouped_df.rename(columns={
        'cantidadPerforacionesPlacas': 'Perforaciones por Placa',
        'perforaTotal': 'Total de Perforaciones'
    })
    grouped_df['mm de perforado'] = grouped_df['Total de Perforaciones'] * grouped_df['espesor']
    grouped_df['costo'] = grouped_df.apply(calculate_price, axis=1)

    return grouped_df.reset_index(drop=True)





def group_and_sum(df, group_columns, avg_column):
    """
    Groups a DataFrame by specified columns and computes the average of another column.

    Parameters:
    - df (pd.DataFrame): The DataFrame to group.
    - group_columns (list): A list of column names to group by.
    - avg_column (str): The name of the column to compute the average for.

    Returns:
    - pd.DataFrame: A DataFrame with the grouped columns and the average values.
    """
    # Group the DataFrame by the specified columns and compute the mean of the avg_column
    grouped_df = df.groupby(group_columns, as_index=False)[avg_column].sum()
    grouped_df[avg_column] = grouped_df[avg_column].round(2)
    return grouped_df

def group_and_avg(df, group_columns, avg_column):
    """
    Groups a DataFrame by specified columns and computes the average of another column.

    Parameters:
    - df (pd.DataFrame): The DataFrame to group.
    - group_columns (list): A list of column names to group by.
    - avg_column (str): The name of the column to compute the average for.

    Returns:
    - pd.DataFrame: A DataFrame with the grouped columns and the average values.
    """
    # Group the DataFrame by the specified columns and compute the mean of the avg_column
    grouped_df = df.groupby(group_columns, as_index=False)[avg_column].mean()
    grouped_df[avg_column] = grouped_df[avg_column].round(2)
    return grouped_df



# Define the sunburst function to create a sunburst plot
def sunburst_plot(df: pd.DataFrame, options: list, name: str, suma: str):
    # Group by the hierarchical structure and compute the mean of 'kg'
    grouped_df = df.groupby(options)[suma].mean().reset_index()

    # Add a root column for the sunburst plot
    grouped_df['root'] = name

    fig = px.sunburst(grouped_df,
                      path=['root'] + options,
                      values= suma,
                      color= suma,
                      color_continuous_scale='Reds',
                      color_discrete_sequence=px.colors.qualitative.G10)

    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)),
                      hovertemplate='<b>%{label}</b><br>tiempo: %{value}')

    fig.update_layout(
        autosize=True,
        coloraxis_colorbar=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3
        )
    )

    return fig


def bar_plot_with_hover_info(df: pd.DataFrame):
    fig = go.Figure()

    # Create bar chart
    fig.add_trace(go.Bar(
        x=df['pv'],
        y=df['placas'],
        text=df['espesor'],  # Add espesor as text annotations
        textposition='outside',  # Position text annotations
        marker=dict(color='LightSkyBlue'),
        hovertemplate=(
            '<b>PV:</b> %{x}<br>'
            '<b>Placas:</b> %{y}<br>'
            '<b>Espesor:</b> %{text}'
        )
    ))

    # Update layout
    fig.update_layout(

        # title='Bar Plot of PV vs. Placas with Espesor Annotations',
        xaxis_title='PV',
        yaxis_title='Placas',
        xaxis=dict(type='category'),
        yaxis=dict(showgrid=True),
        showlegend=False
    )

    # Adjust font size for annotations
    fig.update_traces(textfont_size=12)

    return fig



def bar_plot_with_hover_process(df: pd.DataFrame):
    # Calculate the average time
    average_time = df['Tiempo_Proceso_Dias'].mean()

    # Create bar chart
    fig = go.Figure()

    # Adding bars with correct text annotations
    fig.add_trace(go.Bar(
        x=df['pv'],
        y=df['Tiempo_Proceso_Dias'],
        # text=df['Tiempo Proceso (Dias)'],  # Ensure this is straight from the df
        textposition='outside',
        marker=dict(color='LightSkyBlue'),
        hovertemplate='<b>PV:</b> %{x}<br><b>Tiempo:</b> %{y}<extra></extra>'
    ))

    # Add horizontal line for average time
    fig.add_hline(y=average_time, line_dash="dashdot", line_color="red",
                  annotation_text=f"Average: {average_time:.2f}", annotation_position="bottom right")

    # Update layout
    fig.update_layout(
        title="Dias/Pv en Proceso",
        xaxis_title='PV',
        yaxis_title='Tiempo Proceso (Dias)',
        showlegend=False,
        xaxis=dict(type='category'),
        yaxis=dict(showgrid=True),
        template='plotly_white'  # Setting a clean theme for clear visualization
    )

    return fig






def filter_rows_by_column_value(df, column_name, value_to_kepp, reset_index=True):
    """
    Filters rows from a DataFrame based on a specific column value and optionally resets the index.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    column_name (str): The column to check for the value.
    value_to_drop (str): The value based on which rows will be filtered out.
    reset_index (bool): Whether to reset the index of the resulting DataFrame. Default is True.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    condition = df[column_name] == value_to_kepp
    filtered_df = df[condition]

    if reset_index:
        filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df




def expand_datetime_column(df, column_name):
    """
    Expands a datetime column into separate columns for year, month, day, hour, minute, second, etc.

    Parameters:
    df (pd.DataFrame): The DataFrame to operate on.
    column_name (str): The name of the column containing datetime strings.

    Returns:
    pd.DataFrame: The DataFrame with additional columns for year, month, day, hour, minute, second, etc.
    """
    # Ensure the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    # Convert the column to datetime if it is not already
    df[column_name] = pd.to_datetime(df[column_name])

    # Extracting various parts of the datetime
    df['year'] = df[column_name].dt.year
    df['month'] = df[column_name].dt.month
    df['day'] = df[column_name].dt.day
    df['hour'] = df[column_name].dt.hour
    df['minute'] = df[column_name].dt.minute
    df['espesor'] = df['espesor'].astype(float)
    df['perforaTotal'] = df['perforaTotal'].astype(float)
    return df




def calculate_max_average(df):
    # Group by 'tipoMecanizado', 'maquina', and 'espesor'
    grouped_df = df.groupby(['tipoMecanizado', 'maquina', 'espesor'])

    # Aggregate to find max and average of 'perforaTotal'
    result_df = grouped_df['perforaTotal'].agg(['max', 'mean']).reset_index()

    # Rename columns for clarity
    result_df.columns = ['tipoMecanizado', 'maquina', 'espesor', 'maxPerfora', 'avgPerfora']

    # Round up the values and convert to integer
    result_df['maxPerfora'] = np.ceil(result_df['maxPerfora']).astype(int)
    result_df['avgPerfora'] = np.ceil(result_df['avgPerfora']).astype(int)

    return result_df



def create_perfora_grid(df):
    """
    Creates a grid DataFrame with tipoMecanizado as columns and
    combination of espesor and maquina as rows. Each cell displays
    (maxPerfora, avgPerfora).
    Args:
        df (pd.DataFrame): DataFrame containing the columns 'tipoMecanizado',
        'maquina', 'espesor', 'maxPerfora', 'avgPerfora'.
    Returns:
        pd.DataFrame: Pivot table with the grid layout.
    """
    # Sort the DataFrame by 'espesor', then by 'maquina'
    df_sorted = df.sort_values(by=['espesor', 'maquina'])

    # Create a combined string column for maxPerfora and avgPerfora in the format (max, avg)
    df_sorted['combined'] = df_sorted.apply(lambda x: f"({x['maxPerfora']},{x['avgPerfora']})", axis=1)

    # Create multi-index for rows with espesor and maquina
    df_sorted['row_index'] = list(zip(df_sorted['espesor'], df_sorted['maquina']))

    # Create a pivot table with combined values
    pivot_table = df_sorted.pivot_table(index='row_index', columns='tipoMecanizado', values='combined', aggfunc='first')

    # Reformatting index for a cleaner display
    pivot_table.index = pd.MultiIndex.from_tuples(pivot_table.index, names=['espesor', 'maquina'])

    return pivot_table

# --- Function definitions outside the expander ---
def highlight_na_and_conditions(val):
    try:
        if pd.isna(val):
            return 'background-color: lightcoral; color: black; text-align: center;'
        else:
            max_perfora = float(val)
            if max_perfora > 100:
                return 'background-color: lightgreen; color: black; text-align: center;'
    except:
        pass
    return 'color: black; text-align: center;'

def highlight_espesor_change(df):
    espesor = df.index.get_level_values('espesor')
    bg_colors = pd.DataFrame('', index=df.index, columns=df.columns)
    color_switch = 'lightgrey'
    for i in range(len(espesor)):
        if i == 0 or espesor[i] != espesor[i - 1]:
            color_switch = 'white' if color_switch == 'lightgrey' else 'lightgrey'
        bg_colors.iloc[i] = f'background-color: {color_switch}; color: black; text-align: center;'
    return bg_colors



def get_table_download_link(df, year, month):
    """Generates a link allowing the data in a given pandas dataframe to be downloaded
    in: dataframe
    out: href string
    """
    towrite = BytesIO()
    df.to_excel(towrite, index=False, sheet_name='Sheet1')  # write to BytesIO object
    towrite.seek(0)  # go to the start of the BytesIO object
    b64 = base64.b64encode(towrite.read()).decode()  # encode to base64 (strings <-> bytes conversions)
    filename = f"cnc_{year}_{month}.xlsx"

    # return as button instead of link
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}"><button style="color: black; background-color: #ff6347; border: none; border-radius: 15px; padding: 10px 20px;">Download {year} - {month}</button></a>'

