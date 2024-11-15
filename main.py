import boto3
import streamlit as st

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
months, years, cm, cy = get_months_and_years_since("01/10/2024")

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
    selected_month = st.sidebar.selectbox('Seleccione Mes', months, index=default_month_index)
    selected_year = st.sidebar.selectbox('Seleccione Año', years, index=default_years_index)

# --- Process the data ---
df = create_dataframe_from_items(items)
filtered_df_sabimet = filter_by_year_month(df, selected_year, selected_month, 'sabimet')
filtered_df_steelk = filter_by_year_month(df, selected_year, selected_month, 'steelk')
filtered_df = filter_by_year_month_only(df, selected_year, selected_month)

# --- Overview Section ---
st.markdown("<div class='stHeader'><h1>Kupfer Nave1/CNC Dashboard</h1></div>", unsafe_allow_html=True)
# st.write("Produccion CNC en la Nave1.")

# --- Key Performance Indicators (KPIs) ---
espesor_progress = filter_rows_by_column_value(filtered_df, 'origen', 'Progreso', reset_index=True)
espesor_total = expand_datetime_column(espesor_progress, 'progress_createdAt')
perfora_total = group_and_sum(espesor_total, ['year', 'month', 'day', 'tipoMecanizado', 'espesor'], 'perforaTotal')
df_no_duplicates = drop_all_duplicate_dates(perfora_total, 'year', 'month', 'day')


espesor_m1 = filter_rows_by_column_value(espesor_progress, 'maquina', 'm1', reset_index=True)
perforaciones_m1 = group_and_sum(espesor_m1, ['tipoMecanizado', 'espesor'], 'perforaTotal')
espesor_m1['mm_perforado'] = espesor_m1['espesor'] * espesor_m1['perforaTotal']


avg_mm_m1 = espesor_m1['mm_perforado'].mean()
perfo_m1= espesor_m1["perforaTotal"].sum()
total_mm_m1 = espesor_m1['mm_perforado'].sum()
# Get the count of non-null entries
divisor_mm_m1 = espesor_m1['mm_perforado'].count()

espesor_m2 = filter_rows_by_column_value(espesor_progress, 'maquina', 'm2', reset_index=True)
perforaciones_m2 = group_and_sum(espesor_m2, ['tipoMecanizado', 'espesor'], 'perforaTotal')
espesor_m2['mm_perforado'] = espesor_m2['espesor'] * espesor_m2['perforaTotal']


avg_mm_m2 = espesor_m2['mm_perforado'].mean()
total_mm_m2 = espesor_m2['mm_perforado'].sum()
perfo_m2= espesor_m2["perforaTotal"].sum()
# Get the count of non-null entries
divisor_mm_m2 = espesor_m2['mm_perforado'].count()


espesor_m3 = filter_rows_by_column_value(espesor_progress, 'maquina', 'm3', reset_index=True)
perforaciones_m3 = group_and_sum(espesor_m3, ['tipoMecanizado', 'espesor'], 'perforaTotal')
espesor_m3['mm_perforado'] = espesor_m3['espesor'] * espesor_m3['perforaTotal']

avg_mm_m3 = espesor_m3['mm_perforado'].mean()
total_mm_m3 = espesor_m3['mm_perforado'].sum()
# Get the count of non-null entries
perfo_m3= espesor_m3["perforaTotal"].sum()
divisor_mm_m3 = espesor_m3['mm_perforado'].count()


# Custom CSS for divider lines and cards
st.markdown("""
    <style>
        .metric-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-divider {
            border-top: 1px solid #ddd;
            margin: 10px 0;
        }
        .metric-icon {
            font-size: 24px;
            margin-right: 5px;
        }
        .metric-header {
            color: #007bff;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Creating three columns for organized display
col1, col2, col3 = st.columns(3)


# Function to display metrics with improved text, icons, and dividers
def display_metrics(column, prefix, avg_value, total_value, days_value, perfo_value):
    column.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            {prefix}
        </div>
        <div>
            <span class="metric-icon">📊</span>Promedio. mm/day: {round(avg_value, 2)} mm
        </div>
        <div class="metric-divider"></div>
        <div>
            <span class="metric-icon">📏</span>Total mm: {round(total_value, 2)} mm
        </div>
        <div class="metric-divider"></div>
        <div>
            <span class="metric-icon">📅</span>Reportes: {days_value}
        </div>
        <div class="metric-divider"></div>
        <div>
            <span class="metric-icon">🔧</span>Perforaciones: {perfo_value}
        </div>
    </div>
    """, unsafe_allow_html=True)


# Displaying metrics for M1
display_metrics(col1, "M1 Metrics", avg_mm_m1, total_mm_m1, divisor_mm_m1, perfo_m1)

# Displaying metrics for M2
display_metrics(col2, "M2 Metrics", avg_mm_m2, total_mm_m2, divisor_mm_m2, perfo_m2)

# Displaying metrics for M3
display_metrics(col3, "M3 Metrics", avg_mm_m3, total_mm_m3, divisor_mm_m3, perfo_m3)

# Calculating total values
total_avg_mm = (avg_mm_m1 + avg_mm_m2 + avg_mm_m3) / 3
total_mm = total_mm_m1 + total_mm_m2 + total_mm_m3
total_days = divisor_mm_m1 + divisor_mm_m2 + divisor_mm_m3
total_perfo = perfo_m1 + perfo_m2 + perfo_m3

# Displaying total metrics in a new row
st.markdown("<h3>Totales</h3>", unsafe_allow_html=True)
total_col1, total_col2, total_col3, total_col4 = st.columns(4)


def display_total_metric(column, label, value, icon):
    column.markdown(f"""
    <div class="metric-card">
        <div class="metric-header">
            {label}
        </div>
        <div>
            <span class="metric-icon">{icon}</span>{value}
        </div>
    </div>
    """, unsafe_allow_html=True)


# Total average mm/day
display_total_metric(total_col1, "Promedio. mm/day", f"{round(total_avg_mm, 2)} mm", "📊")

# Total mm
display_total_metric(total_col2, "Total mm", f"{round(total_mm, 2)} mm", "📏")

# Total number of days
display_total_metric(total_col3, "Reportes", total_days, "📅")

# Total perforaciones
display_total_metric(total_col4, "Perforaciones", total_perfo, "🔧")

# --- Perforaciones Grid Visualization ---
with st.expander("Perfil General Perforaciones", expanded=False):

    columns_to = [
        'pv', 'Inicio', 'cantidadPerforacionesTotal', 'Terminado', 'cantidadPerforacionesPlacas',
        'kg', 'progress_createdAt', 'origen', 'placas', 'hora_reporte', 'tiempo', 'tiempo_seteo', 'negocio',
        'Tiempo Proceso (min)', 'minute'
    ]
    perforaciones_day_tipo = (espesor_total.drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')).drop(
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
    - El fondo de la fila cambia cuando cambia el valor de espesor.""")


# ... (Your existing code for the dashboard) ...

# --- Perfil Tipo M1, M2, M3 and General Perfil DataFrames ---
with st.expander("Perforaciones por Maquina", expanded=False):
    # Create three columns for M1, M2, and M3
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("M1/Perfil")
        df_perfil_tipoM_m1 = perforaciones_m1.sort_values('perforaTotal',
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
        df_perfil_tipoM_m2 = perforaciones_m2.sort_values('perforaTotal',
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
        df_perfil_tipoM_m3 = perforaciones_m3.sort_values('perforaTotal',
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

# Convert the 'espesor' column to Decimal
filtered_df_steelk['espesor'] = filtered_df_steelk['espesor'].apply(Decimal)
filtered_df_steelk['mm totales'] = filtered_df_steelk['perforaTotal'].apply(Decimal) * filtered_df_steelk['espesor']

# Convert the 'espesor' column to Decimal
filtered_df_sabimet['espesor'] = filtered_df_sabimet['espesor'].apply(Decimal)
filtered_df_sabimet['mm totales'] = filtered_df_sabimet['perforaTotal'].apply(Decimal) * filtered_df_sabimet['espesor']


perfora_filtered_df_sabimet =filtered_df_sabimet['perforaTotal'].sum()
mm_filtered_df_sabimet =filtered_df_sabimet['mm totales'].sum()

perfo_filtered_df_steelk = filtered_df_steelk['perforaTotal'].sum()
mm_filtered_df_steelk = filtered_df_steelk['mm totales'].sum()


# Custom CSS for divider lines and cards
st.markdown("""
    <style>
        .metric-row {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            flex: 1;
            margin-bottom: 10px;
            min-width: 200px;
        }
        .metric-header {
            color: #007bff;
            font-weight: bold;
            text-align: center;
        }
        .metric-content {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)


# Function to display summed values in one row
def display_summed_metrics_single_row(prefix, perfo_sum, mm_sum):
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-header">{prefix} Total Perforaciones</div>
            <div class="metric-content">
                🔧 {perfo_sum}
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-header">{prefix} Total mm</div>
            <div class="metric-content">
                📏 {round(mm_sum, 2)} mm
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)



st.header("Sabimet Analysis")
# Displaying summed metrics for Sabimet
display_summed_metrics_single_row("Sabimet", perfora_filtered_df_sabimet, mm_filtered_df_sabimet)

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
# Displaying summed metrics for Steelk
display_summed_metrics_single_row("Steelk", perfo_filtered_df_steelk, mm_filtered_df_steelk)


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