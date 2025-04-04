import boto3
import streamlit as st
from util_functions import *  # Import all functions from util_functions.py

# Initialize DynamoDB resource
dynamo = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamo.Table('sam-stack-irlaa-MecanizadoCloseTable-1IKYW80FKFRII')

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

def show_no_data_message(title, month, year):
    st.markdown(f"""
        <style>
        .no-data-container {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 2rem;
            margin: 2rem 0;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .no-data-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
            color: #6c757d;
        }}
        .no-data-title {{
            color: #343a40;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            font-weight: 500;
        }}
        .no-data-message {{
            color: #6c757d;
            font-size: 1rem;
            margin-bottom: 0.5rem;
            line-height: 1.5;
        }}
        .no-data-suggestion {{
            color: #0066cc;
            font-size: 0.9rem;
            margin-top: 1rem;
            padding: 0.5rem;
            background-color: #f1f8ff;
            border-radius: 4px;
            display: inline-block;
        }}
        </style>
        <div class="no-data-container">
            <div class="no-data-icon">📊</div>
            <div class="no-data-title">No hay datos disponibles para {title}</div>
            <div class="no-data-message">
                No se encontraron registros para el mes {month} del año {year}.
            </div>
            <div class="no-data-message">
                Por favor, seleccione un período diferente o verifique que existan datos para este período.
            </div>
            <div class="no-data-suggestion">
                💡 Intente seleccionar otro rango de fechas
            </div>
        </div>
    """, unsafe_allow_html=True)


# --- Enhanced Sidebar with Light Effects ---
with st.sidebar:
    st.markdown("""
        <style>
        [data-testid=stSidebar] {
            background: linear-gradient(135deg, #f5f7fa 0%, #e3e6e8 100%);
        }
        
        /* Shimmer effect base */
        @keyframes shimmer {
            0% {
                background-position: -1000px 0;
            }
            100% {
                background-position: 1000px 0;
            }
        }
        
        /* Glow effect */
        @keyframes glow {
            0% { box-shadow: 0 0 5px rgba(78, 205, 196, 0.2); }
            50% { box-shadow: 0 0 20px rgba(78, 205, 196, 0.4); }
            100% { box-shadow: 0 0 5px rgba(78, 205, 196, 0.2); }
        }
        
        /* Light beam effect */
        @keyframes lightBeam {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(100%) rotate(45deg); }
        }
        
        .logo-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                45deg,
                transparent,
                rgba(255,255,255,0.8),
                transparent
            );
            transform: rotate(45deg);
            animation: lightBeam 3s infinite;
        }
        
        .logo-container:hover {
            transform: translateY(-5px);
            animation: glow 2s infinite;
        }
        
        .dashboard-title {
            position: relative;
            background: #0a1f2b;  /* Using the darkest option */
            color: white;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            padding: 20px 0;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(13, 43, 54, 0.3);
        }
        
            
        .dashboard-title::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,0.8),
                transparent
            );
            animation: shimmer 3s infinite;
        }
        
        .time-period-container {
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            position: relative;
            overflow: hidden;
        }
        
        .time-period-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                45deg,
                transparent,
                rgba(255,255,255,0.4),
                transparent
            );
            transform: rotate(45deg);
            transition: 0.5s;
        }
        
        .time-period-container:hover::before {
            animation: lightBeam 2s;
        }
        
        .stSelectbox > div > div {
            background: white !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            border-radius: 8px !important;
            transition: all 0.3s ease;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #2193b0 !important;
            box-shadow: 0 0 15px rgba(33, 147, 176, 0.2) !important;
        }
        
        .section-title {
            color: #2193b0;
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
            position: relative;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, #2193b0, transparent);
        }
        
        .info-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            position: relative;
            overflow: hidden;
        }
        
        .info-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,0.8),
                transparent
            );
            animation: shimmer 4s infinite;
        }
        
        /* Custom scrollbar */
        [data-testid=stSidebar]::-webkit-scrollbar {
            width: 6px;
            background: transparent;
        }
        
        [data-testid=stSidebar]::-webkit-scrollbar-thumb {
            background: rgba(33, 147, 176, 0.2);
            border-radius: 3px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Logo Section with light effects
    st.markdown("""
        <div>
            <div style="position: relative;">
    """, unsafe_allow_html=True)
    st.image("data/logo.png", use_container_width=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Dashboard Title with shimmer
    st.markdown("""
        <div class="dashboard-title">
            📊 Nave1/CNC Dashboard
        </div>
    """, unsafe_allow_html=True)
    # Time Period Section with light beam effect
    st.markdown("""
        <div class="time-period-container">
            <div class="section-title">
                <span>📅</span> Time Period
            </div>
    """, unsafe_allow_html=True)

    # Month and Year Selection
    if cm == 1:
        default_month_index = months.index(cm)
    else:
        default_month_index = months.index(cm) - 1

    default_years_index = years.index(cy)

    selected_month = st.selectbox(
        'Select Month',
        months,
        index=default_month_index,
        key='month_selector'
    )

    selected_year = st.selectbox(
        'Select Year',
        years,
        index=default_years_index,
        key='year_selector'
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Info Section with shimmer effect
    st.markdown("""
        <div class="info-container">
            <div class="section-title">
                <span>ℹ️</span> Dashboard Info
            </div>
            <div style="color: #666; font-size: 14px;">
                Last updated: Today<br>
                Status: Live
            </div>
        </div>
    """, unsafe_allow_html=True)


# --- Process the data ---
df = create_dataframe_from_items(items)
filtered_df_sabimet = filter_by_year_month(df, selected_year, selected_month, 'sabimet')
filtered_df_steelk = filter_by_year_month(df, selected_year, selected_month, 'steelk')
filtered_df = filter_by_year_month_only(df, selected_year, selected_month)



if not filtered_df.empty:
    # --- Overview Section ---
    st.markdown("<div class='stHeader'><h1>Kupfer Nave1/CNC Dashboard</h1></div>", unsafe_allow_html=True)
    # st.write("Produccion CNC en la Nave1.")

    # --- Key Performance Indicators (KPIs) ---
    espesor_progress = filter_rows_by_column_value(filtered_df, 'origen', 'Progreso', reset_index=True)
    # print(espesor_progress.columns)
    # total_columns ['pv', 'Inicio', 'cantidadPerforacionesTotal', 'Terminado',
    #    'cantidadPerforacionesPlacas', 'kg', 'tipoMecanizado',
    #    'progress_createdAt', 'origen', 'maquina', 'placas', 'hora_reporte',
    #    'tiempo', 'tiempo_seteo', 'espesor', 'negocio', 'cliente',
    #    'perforaTotal', 'Tiempo Proceso (min)']

    columns_to_drop_download = [ 'Inicio','progress_createdAt', 'origen', 'maquina', 'tiempo', 'tiempo_seteo',
                                 'hora_reporte', 'Tiempo Proceso (min)']


    columns_to_drop_download2 = [ 'cantidadPerforacionesTotal', 'posicion', 'kg','Perforaciones por Placa', 'placas',
                                  'tipoMecanizado']

    columns_to_drop_download3 = ['cantidadPerforacionesTotal', 'posicion', 'kg', 'tipoMecanizado']

    df_to_download = espesor_progress.drop(columns=columns_to_drop_download)



    df_to_download3 = group_and_sum_without_remove_columns(df_to_download,
                                                           ['pv', 'posicion'],
                                                           ['perforaTotal', 'placas'])

    df_to_download2 = group_and_sum_without_remove_columns2(df_to_download3,
                                                           ['pv'],
                                                           ['perforaTotal',
                                                            'mm de perforado', 'costo'])


    # Rename columns
    df_to_download2 = df_to_download2.rename(columns={
        'cantidadPerforacionesPlacas': 'Perforaciones por Placa',
        'perforaTotal': 'Total de Perforaciones'
    })

    df_to_download3 = df_to_download3.rename(columns={
        'cantidadPerforacionesPlacas': 'Perforaciones por Placa',
        'perforaTotal': 'Total de Perforaciones'
    })

    df_to_download2 = df_to_download2.drop(columns=columns_to_drop_download2)
    df_to_download3 = df_to_download3.drop(columns=columns_to_drop_download3)
    # Add the download button for DataFrame
    df_to_download2['Terminado'] = df_to_download2['Terminado'].dt.strftime('%Y-%m-%d')
    df_to_download3['Terminado'] = df_to_download3['Terminado'].dt.strftime('%Y-%m-%d')

    with st.expander("Archivos para descargar", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(get_table_download_link(
                df_to_download2,
                selected_year,
                selected_month,
                'Resumen'
            ), unsafe_allow_html=True)

        with col2:
            st.markdown(get_table_download_link(
                df_to_download3,
                selected_year,
                selected_month,
                'Total'
            ), unsafe_allow_html=True)

    espesor_total = expand_datetime_column(espesor_progress, 'progress_createdAt')

    perfora_total = group_and_sum(espesor_total, ['t'
                                                  'ipoMecanizado', 'espesor'], 'perforaTotal')

    mm_T = espesor_total['espesor'] * espesor_total['perforaTotal']

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
                <span class="metric-icon">📊</span>mm/day: {round(avg_value, 2)} mm
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
    total_perfo =perfo_m1 + perfo_m2 + perfo_m3

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
        df_total = filter_rows_by_column_value(df, 'origen', 'Progreso', reset_index=True)
        df_total = expand_datetime_column(df_total, 'progress_createdAt')

        columns_to = [
            'pv', 'Inicio', 'cantidadPerforacionesTotal', 'Terminado', 'cantidadPerforacionesPlacas',
            'kg', 'progress_createdAt', 'origen', 'placas', 'hora_reporte', 'tiempo', 'tiempo_seteo', 'negocio',
            'Tiempo Proceso (min)', 'minute'
        ]
        perforaciones_day_tipo = ( df_total.drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')).drop(
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
        # --- Key Performance Indicators (KPIs) ---


        df_perfil_tipoM = group_and_avg(perfora_total, ['tipoMecanizado', 'espesor'],
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


# --- Sabimet Analysis ---
if not filtered_df_sabimet.empty:
    st.header("Sabimet Analysis")

    # Data preprocessing
    filtered_df_sabimet['espesor'] = filtered_df_sabimet['espesor'].apply(Decimal)
    filtered_df_sabimet['mm totales'] = filtered_df_sabimet['perforaTotal'].apply(Decimal) * filtered_df_sabimet['espesor']

    # Calculate metrics
    perfora_filtered_df_sabimet = filtered_df_sabimet['perforaTotal'].sum()
    mm_filtered_df_sabimet = filtered_df_sabimet['mm totales'].sum()

    # Display metrics
    display_summed_metrics_single_row("Sabimet", perfora_filtered_df_sabimet, mm_filtered_df_sabimet)

    # Process time analysis
    columns_to_drop = [
        'Inicio', 'cantidadPerforacionesTotal', 'Terminado', 'cantidadPerforacionesPlacas',
        'kg', 'tipoMecanizado', 'progress_createdAt', 'origen', 'maquina', 'placas',
        'hora_reporte', 'tiempo', 'tiempo_seteo', 'espesor', 'negocio', 'perforaTotal',
        'Tiempo Proceso (min)'
    ]

    df_sabimet_process_time = (filtered_df_sabimet
        .drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')
        .assign(Tiempo_Proceso_Dias=lambda x: (x['Tiempo Proceso (min)'] / (60 * 24)).round(2))
        .drop(columns=columns_to_drop)
        .groupby('pv', as_index=False)['Tiempo_Proceso_Dias'].sum()
        .sort_values('Tiempo_Proceso_Dias', ascending=False)
        .reset_index(drop=True))

    # Group and plot data
    grouped_df_sabimet = (group_and_sum(filtered_df_sabimet, ['pv', 'espesor'], 'placas')
        .groupby(['pv', 'espesor'], as_index=False)['placas'].sum()
        .sort_values('placas', ascending=False)
        .reset_index(drop=True))

    # Create and display plots
    fig = bar_plot_with_hover_info(grouped_df_sabimet)
    st.plotly_chart(fig)

    st.header("Sabimet Procesos")
    fig = bar_plot_with_hover_process(df_sabimet_process_time)
    st.plotly_chart(fig)
else:
    show_no_data_message("Sabimet", selected_month, selected_year)

# --- Steelk Analysis ---
if not filtered_df_steelk.empty:
    st.header("Steelk Analysis")

    # Data preprocessing
    filtered_df_steelk['espesor'] = filtered_df_steelk['espesor'].apply(Decimal)
    filtered_df_steelk['mm totales'] = filtered_df_steelk['perforaTotal'].apply(Decimal) * filtered_df_steelk['espesor']

    # Calculate metrics
    perfo_filtered_df_steelk = filtered_df_steelk['perforaTotal'].sum()
    mm_filtered_df_steelk = filtered_df_steelk['mm totales'].sum()

    # Display metrics
    display_summed_metrics_single_row("Steelk", perfo_filtered_df_steelk, mm_filtered_df_steelk)

    # Process time analysis
    df_steelk_process_time = (filtered_df_steelk
        .drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')
        .assign(Tiempo_Proceso_Dias=lambda x: (x['Tiempo Proceso (min)'] / (60 * 24)).round(2))
        .drop(columns=columns_to_drop)
        .groupby('pv', as_index=False)['Tiempo_Proceso_Dias'].sum()
        .sort_values('Tiempo_Proceso_Dias', ascending=False)
        .reset_index(drop=True))

    # Group and plot data
    grouped_df_steelk = (group_and_sum(filtered_df_steelk, ['pv', 'espesor'], 'placas')
        .groupby(['pv', 'espesor'], as_index=False)['placas'].sum()
        .sort_values('placas', ascending=False)
        .reset_index(drop=True))

    # Create and display plots
    fig = bar_plot_with_hover_info(grouped_df_steelk)
    st.plotly_chart(fig)

    st.header("Steelk Procesos")
    fig = bar_plot_with_hover_process(df_steelk_process_time)
    st.plotly_chart(fig)
else:
    show_no_data_message("Steelk", selected_month, selected_year)
