import boto3
import streamlit as st
import pandas as pd
import plotly.express as px

from util_functions import *  # Import all functions from util_functions.py

# Initialize DynamoDB resource
dynamo = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamo.Table('MECANIZADO_CLOSE2-dev')

# Scan the DynamoDB table and retrieve all items
response = table.scan()
items = response['Items']

while 'LastEvaluatedKey' in response:
    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    items.extend(response['Items'])

# Get months and years since a particular date
months, years, cm, cy = get_months_and_years_since("01/08/2024")

# Streamlit configuration for the web app
st.set_page_config(
    page_title="Dashboard/CNC",
    page_icon="📉",
    layout="wide"
)

# --- CSS Styling ---
st.markdown("""
<style>
/* General Styling */
body, h1, h2, h3, h4, .stMetric label, .stMetric div[data-testid="stMetricValue"], .stDataFrame, p {
    color: #000000 !important; 
    font-family: 'Arial', sans-serif;
}
body {
    background-color: #f4f4f4;
}
.stApp {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Header Styling */
.stHeader {
    background-color: #e9ecef;  
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 15px;
}

/* Metric Styling */
.stMetric {
    border: 1px solid #e0e0e0;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}
div[data-testid="metric-container"] > div[data-testid="stMetricValue"] {
    font-size: 24px !important; 
    font-weight: bold !important; 
}

/* Plot Styling */
.plotly-graph-svg {
    background-color: #ffffff;
}
.plotly-graph-svg text { 
    fill: #000000 !important; 
} 

/* Expander Styling */
.stExpanderHeader {
    background-color: #e9ecef;
    padding: 10px;
    border-radius: 5px;
    font-weight: bold;
    border: 1px solid #cccccc; 
}
</style>
""", unsafe_allow_html=True)


# --- Sidebar setup ---
with st.sidebar:
    st.sidebar.image("data/logo.png", use_column_width=True)
    st.title("📅 Nave1/CNC Dashboard")
    default_month_index = months.index(cm) - 1
    default_years_index = years.index(cy)
    selected_month = st.sidebar.selectbox('Selecciones Mes', months, index=default_month_index)
    selected_year = st.sidebar.selectbox('Selecciones Año', years, index=default_years_index)

# --- Process the data ---
df = create_dataframe_from_items(items)
filtered_df_sabimet = filter_by_year_month(df, selected_year, selected_month, 'sabimet')
filtered_df_steelk = filter_by_year_month(df, selected_year, selected_month, 'steelk')

# --- Overview Section ---
st.markdown("<div class='stHeader'><h1>Kupfer Nave1/CNC Dashboard</h1></div>", unsafe_allow_html=True)
st.write("Produccion CNC en la Nave1.")

# --- Key Performance Indicators (KPIs) ---
espesor_progress = filter_rows_by_column_value(filtered_df_sabimet, 'origen', 'Progreso', reset_index=True)
espesor_total = expand_datetime_column(espesor_progress, 'progress_createdAt')
espesor_total = group_and_sum(espesor_total, ['year', 'month', 'day', 'tipoMecanizado', 'espesor'], 'perforaTotal')
df_no_duplicates = drop_all_duplicate_dates(espesor_total, 'year', 'month', 'day')

espesor_m1 = filter_rows_by_column_value(espesor_progress, 'maquina', 'm1', reset_index=True)
espesor_m1 = expand_datetime_column(espesor_m1, 'progress_createdAt')
espesor_m1 = group_and_sum(espesor_m1, ['year', 'month', 'day', 'tipoMecanizado', 'espesor'], 'perforaTotal')
df_no_duplicates_m1 = drop_all_duplicate_dates(espesor_m1, 'year', 'month', 'day')
espesor_m1['mm_perforado'] = espesor_m1['espesor'] * espesor_m1['perforaTotal']
espesor_m1 = group_and_sum(espesor_m1, ['year', 'month', 'day'], 'mm_perforado')
avg_mm_m1 = espesor_m1['mm_perforado'].mean()

espesor_m2 = filter_rows_by_column_value(espesor_progress, 'maquina', 'm2', reset_index=True)
espesor_m2 = expand_datetime_column(espesor_m2, 'progress_createdAt')
espesor_m2 = group_and_sum(espesor_m2, ['year', 'month', 'day', 'tipoMecanizado', 'espesor'], 'perforaTotal')
df_no_duplicates_m2 = drop_all_duplicate_dates(espesor_m2, 'year', 'month', 'day')
espesor_m2['mm_perforado'] = espesor_m2['espesor'] * espesor_m2['perforaTotal']
espesor_m2 = group_and_sum(espesor_m2, ['year', 'month', 'day'], 'mm_perforado')
avg_mm_m2 = espesor_m2['mm_perforado'].mean()

espesor_m3 = filter_rows_by_column_value(espesor_progress, 'maquina', 'm3', reset_index=True)
espesor_m3 = expand_datetime_column(espesor_m3, 'progress_createdAt')
espesor_m3 = group_and_sum(espesor_m3, ['year', 'month', 'day', 'tipoMecanizado', 'espesor'], 'perforaTotal')
df_no_duplicates_m3 = drop_all_duplicate_dates(espesor_m3, 'year', 'month', 'day')
espesor_m3['mm_perforado'] = espesor_m3['espesor'] * espesor_m3['perforaTotal']
espesor_m3 = group_and_sum(espesor_m3, ['year', 'month', 'day'], 'mm_perforado')
avg_mm_m3 = espesor_m3['mm_perforado'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Average mm/day on M1", f"{round(avg_mm_m1, 2)}")
with col2:
    st.metric("Average mm/day on M2", f"{round(avg_mm_m2, 2)}")
with col3:
    st.metric("Average mm/day on M3", f"{round(avg_mm_m3, 2)}")
# --- Perforaciones Grid Visualization ---
with st.expander("Perforaciones", expanded=False):





    perforaciones_day_tipo = filter_rows_by_column_value(df, 'origen', 'Progreso', reset_index=True)
    perforaciones_day_tipo = expand_datetime_column(perforaciones_day_tipo, 'progress_createdAt')
    columns_to = [
        'pv', 'Inicio', 'cantidadPerforacionesTotal', 'Terminado', 'cantidadPerforacionesPlacas',
        'kg', 'progress_createdAt', 'origen', 'placas', 'hora_reporte', 'tiempo', 'tiempo_seteo', 'negocio',
        'Tiempo Proceso (min)', 'minute'
    ]
    perforaciones_day_tipo = (perforaciones_day_tipo.drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')).drop(
        columns=columns_to)
    perforaciones_day_tipo = calculate_max_average(perforaciones_day_tipo)
    grid = create_perfora_grid(perforaciones_day_tipo)

    # --- Styling the DataFrame ---
    grid = grid.style.format(precision=2)  # Format numbers to two decimal places
    grid = grid.applymap(highlight_na_and_conditions) # Apply existing color conditions
    grid = grid.apply(highlight_espesor_change, axis=None) # Apply existing row highlighting
    grid = grid.set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#f0f2f5'), ('font-size', '14px'), ('text-align', 'center')]}, # Style headers
        {'selector': 'td', 'props': [('font-size', '12px'), ('text-align', 'center')]}, # Style cells
        {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]}, # Style table
        {'selector': 'th, td', 'props': [('border', '1px solid #ddd'), ('padding', '8px')]} # Add borders and padding
    ])

    # --- Interactive Table with st.dataframe ---
    st.dataframe(grid, height=400, use_container_width=True)

    st.text("""Note: 
    - (Maximo, Media)
    - El fondo de la fila cambia cuando cambia el valor de espesor.
    - Las celdas se resaltan basadas en ciertas condiciones.
    - Los encabezados están estilizados para una mejor visibilidad. """)


# ... (Your existing code for the dashboard) ...

# --- Perfil Tipo M1, M2, M3 and General Perfil DataFrames ---
with st.expander("Perfil Analysis", expanded=False):
    # Create three columns for M1, M2, and M3
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("M1/Perfil")
        df_perfil_tipoM_m1 = group_and_avg(df_no_duplicates_m1, ['tipoMecanizado', 'espesor'],
                                          'perforaTotal').sort_values('perforaTotal',
                                                                      ascending=False).reset_index(drop=True)
        # Style the DataFrame
        df_perfil_tipoM_m1 = df_perfil_tipoM_m1.style.format(precision=2)
        df_perfil_tipoM_m1 = df_perfil_tipoM_m1.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f0f2f5'), ('font-size', '14px'), ('text-align', 'center')]},
            {'selector': 'td', 'props': [('font-size', '12px'), ('text-align', 'center')]},
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
            {'selector': 'th, td', 'props': [('border', '1px solid #ddd'), ('padding', '8px')]}
        ])
        st.dataframe(df_perfil_tipoM_m1, height=200, use_container_width=True)

    with col2:
        st.subheader("M2/Perfil")
        df_perfil_tipoM_m2 = group_and_avg(df_no_duplicates_m2, ['tipoMecanizado', 'espesor'],
                                          'perforaTotal').sort_values('perforaTotal',
                                                                      ascending=False).reset_index(drop=True)
        # Apply the same styling and st.dataframe() to df_perfil_tipoM_m2
        df_perfil_tipoM_m2 = df_perfil_tipoM_m2.style.format(precision=2)
        df_perfil_tipoM_m2 = df_perfil_tipoM_m2.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f0f2f5'), ('font-size', '14px'), ('text-align', 'center')]},
            {'selector': 'td', 'props': [('font-size', '12px'), ('text-align', 'center')]},
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
            {'selector': 'th, td', 'props': [('border', '1px solid #ddd'), ('padding', '8px')]}
        ])
        st.dataframe(df_perfil_tipoM_m2, height=200, use_container_width=True)

    with col3:
        st.subheader("M3/Perfil")
        df_perfil_tipoM_m3 = group_and_avg(df_no_duplicates_m3, ['tipoMecanizado', 'espesor'],
                                          'perforaTotal').sort_values('perforaTotal',
                                                                      ascending=False).reset_index(drop=True)
        # Apply the same styling and st.dataframe() to df_perfil_tipoM_m3
        df_perfil_tipoM_m3 = df_perfil_tipoM_m3.style.format(precision=2)
        df_perfil_tipoM_m3 = df_perfil_tipoM_m3.set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#f0f2f5'), ('font-size', '14px'), ('text-align', 'center')]},
            {'selector': 'td', 'props': [('font-size', '12px'), ('text-align', 'center')]},
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
            {'selector': 'th, td', 'props': [('border', '1px solid #ddd'), ('padding', '8px')]}
        ])
        st.dataframe(df_perfil_tipoM_m3, height=200, use_container_width=True)

    # Create a single column (full width) for "GENERAL PERFIL"
    st.subheader("PERFIL GENERAL")

    df_perfil_tipoM = group_and_avg(df_no_duplicates, ['tipoMecanizado', 'espesor'],
                                       'perforaTotal').sort_values('perforaTotal',
                                                                   ascending=False).reset_index(drop=True)
    # Apply the same styling and st.dataframe() to df_perfil_tipoM_m3
    df_perfil_tipoM = df_perfil_tipoM.style.format(precision=2)
    df_perfil_tipoM = df_perfil_tipoM.set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#f0f2f5'), ('font-size', '14px'), ('text-align', 'center')]},
        {'selector': 'td', 'props': [('font-size', '12px'), ('text-align', 'center')]},
        {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
        {'selector': 'th, td', 'props': [('border', '1px solid #ddd'), ('padding', '8px')]}
    ])


    st.dataframe(df_perfil_tipoM, height=200, use_container_width=True) # You can choose which DF to show here

# --- Sabimet and Steelk Analysis ---
st.header("Sabimet Analysis")
grouped_df_sabimet = group_and_sum(filtered_df_sabimet, ['pv', 'espesor'], 'placas').sort_values('placas',
                                                                                                ascending=False).reset_index(
    drop=True)
columns_to_drop = [
    'Inicio', 'cantidadPerforacionesTotal', 'Terminado', 'cantidadPerforacionesPlacas',
    'kg', 'tipoMecanizado', 'progress_createdAt', 'origen', 'maquina', 'placas',
    'hora_reporte', 'tiempo', 'tiempo_seteo', 'espesor', 'negocio', 'perforaTotal',
    'Tiempo Proceso (min)'
]
df_sabimet_process_time = (filtered_df_sabimet.drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')
                           .assign(Tiempo_Proceso_Dias=lambda x: (x['Tiempo Proceso (min)'] / (60 * 24)).round(2))
                           .drop(columns=columns_to_drop)
                           .groupby('pv', as_index=False)['Tiempo_Proceso_Dias'].sum()
                           .sort_values('Tiempo_Proceso_Dias', ascending=False)
                           .reset_index(drop=True))
grouped_df_sabimet = grouped_df_sabimet.groupby(['pv', 'espesor'], as_index=False)['placas'].sum().sort_values('placas',
                                                                                                            ascending=False).reset_index(
    drop=True)
fig = bar_plot_with_hover_info(grouped_df_sabimet)
st.plotly_chart(fig)

st.header("Sabimet Procesos")
fig = bar_plot_with_hover_process(df_sabimet_process_time)
st.plotly_chart(fig)

# --- Steelk Analysis ---
st.header("Steelk Analysis")
grouped_df_steelk = group_and_sum(filtered_df_steelk, ['pv', 'espesor'], 'placas').sort_values('placas',
                                                                                                ascending=False).reset_index(
    drop=True)
df_steelk_process_time = (filtered_df_steelk.drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')
                           .assign(Tiempo_Proceso_Dias=lambda x: (x['Tiempo Proceso (min)'] / (60 * 24)).round(2))
                           .drop(columns=columns_to_drop)
                           .groupby('pv', as_index=False)['Tiempo_Proceso_Dias'].sum()
                           .sort_values('Tiempo_Proceso_Dias', ascending=False)
                           .reset_index(drop=True))
grouped_df_steelk = grouped_df_steelk.groupby(['pv', 'espesor'], as_index=False)['placas'].sum().sort_values('placas',
                                                                                                            ascending=False).reset_index(
    drop=True)
fig = bar_plot_with_hover_info(grouped_df_steelk)
st.plotly_chart(fig)

st.header("Steelk Procesos")
fig = bar_plot_with_hover_process(df_steelk_process_time)
st.plotly_chart(fig)

# --- Tiempo/Placa and Tiempo Seteo/Placa Sunburst Plots ---
st.header("Tiempo/Placa Analysis")
columns_to_drop = [
    'pv', 'Inicio', 'cantidadPerforacionesTotal', 'Terminado',
    'progress_createdAt', 'origen', 'placas', 'hora_reporte',
    'perforaTotal', 'Tiempo Proceso (min)'
]
tiempo_seteo_sabimet = filter_and_drop_columns(filtered_df_sabimet, 'tiempo_seteo', 0, columns_to_drop)
tiempo_seteo_steelk = filter_and_drop_columns(filtered_df_steelk, 'tiempo_seteo', 0, columns_to_drop)
group_columns = ['maquina', 'tipoMecanizado', 'espesor']
avg_column = 'tiempo'
grouped_df_sabimet = group_and_average(tiempo_seteo_sabimet, group_columns, avg_column)
grouped_df_steelk = group_and_average(tiempo_seteo_steelk, group_columns, avg_column)
tiempo_seteo_sabimet['negocio'] = 'Sabimet'
tiempo_seteo_steelk['negocio'] = 'Stelk'
df_negocio = pd.concat([tiempo_seteo_sabimet, tiempo_seteo_steelk])

fig = sunburst_plot(df_negocio, ['negocio'] + group_columns, 'Negocio', 'tiempo')
st.plotly_chart(fig)

st.header("Tiempo Seteo/Placa Analysis")
fig = sunburst_plot(df_negocio, ['negocio'] + group_columns, 'Negocio', 'tiempo_seteo')
st.plotly_chart(fig)