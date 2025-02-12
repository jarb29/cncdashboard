import boto3
import streamlit as st
from util_functions import *  # Import all functions from util_functions.py
from decimal import Decimal

# --- Initialize DynamoDB and Data Retrieval ---
def initialize_database():
    dynamo = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamo.Table('sam-stack-irlaa-MecanizadoCloseTable-1IKYW80FKFRII')
    return table

def get_all_items(table):
    response = table.scan()
    items = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    return items

# --- Page Configuration ---
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
def display_summed_metrics_single_row(company_name, perforaciones, mm_totales):
    """
    Display metrics in a single row using columns
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label=f"Total Perforaciones {company_name}",
            value=f"{int(perforaciones):,}"
        )
    
    with col2:
        st.metric(
            label=f"Total mm {company_name}",
            value=f"{int(mm_totales):,}"
        )

# --- Main Function ---
def main():
    # Initialize database and get data
    table = initialize_database()
    items = get_all_items(table)
    
    # Get months and years since a particular date
    months, years, cm, cy = get_months_and_years_since("01/10/2024")
    
    # --- Sidebar setup ---
    with st.sidebar:
        st.sidebar.image("data/logo.png", use_container_width=True)
        st.title("📅 Nave1/CNC Dashboard")
        
        # Handle month selection
        if cm == 1:
            default_month_index = months.index(cm)
        else:
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

    # --- Perforaciones Grid Visualization ---
    with st.expander("Perfil General Perforaciones", expanded=False):
        if filtered_df.empty:
            st.error("⚠️ No data available for the selected period")
        else:
            df_total = filter_rows_by_column_value(df, 'origen', 'Progreso', reset_index=True)
            df_total = expand_datetime_column(df_total, 'progress_createdAt')
            
            columns_to = [
                'pv', 'Inicio', 'cantidadPerforacionesTotal', 'Terminado', 'cantidadPerforacionesPlacas',
                'kg', 'progress_createdAt', 'origen', 'placas', 'hora_reporte', 'tiempo', 'tiempo_seteo', 'negocio',
                'Tiempo Proceso (min)', 'minute'
            ]
            
            perforaciones_day_tipo = (df_total.drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')).drop(
                columns=columns_to)
            perforaciones_day_tipo = calculate_max_average(perforaciones_day_tipo)
            grid = create_perfora_grid(perforaciones_day_tipo)

            # Styling the DataFrame
            grid = grid.style.format(precision=2)
            grid = grid.applymap(highlight_na_and_conditions)
            grid = grid.apply(highlight_espesor_change, axis=None)
            grid = grid.set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#f0f2f5'), ('font-size', '14px'), ('text-align', 'center')]},
                {'selector': 'td', 'props': [('font-size', '12px'), ('text-align', 'center')]},
                {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
                {'selector': 'th, td', 'props': [('border', '1px solid #ddd'), ('padding', '8px')]}
            ])

            st.dataframe(grid, height=400, use_container_width=True)
            st.text("""Note: 
            - (Maximo, Media)
            - El fondo de la fila cambia cuando cambia el valor de espesor.""")

    # --- Sabimet Analysis ---
    st.header("Sabimet Analysis")
    if filtered_df_sabimet.empty:
        st.error("⚠️ No data available for Sabimet with the selected filters")
    else:
        # Process Sabimet data
        filtered_df_sabimet['espesor'] = filtered_df_sabimet['espesor'].apply(Decimal)
        filtered_df_sabimet['mm totales'] = filtered_df_sabimet['perforaTotal'].apply(Decimal) * filtered_df_sabimet['espesor']
        
        perfora_filtered_df_sabimet = filtered_df_sabimet['perforaTotal'].sum()
        mm_filtered_df_sabimet = filtered_df_sabimet['mm totales'].sum()
        
        # Display Sabimet metrics and visualizations
        display_summed_metrics_single_row("Sabimet", perfora_filtered_df_sabimet, mm_filtered_df_sabimet)
        
        # Process and display Sabimet charts
        grouped_df_sabimet = process_and_display_charts(filtered_df_sabimet, "Sabimet")

    # --- Steelk Analysis ---
    st.header("Steelk Analysis")
    if filtered_df_steelk.empty:
        st.error("⚠️ No data available for Steelk with the selected filters")
    else:
        # Process Steelk data
        filtered_df_steelk['espesor'] = filtered_df_steelk['espesor'].apply(Decimal)
        filtered_df_steelk['mm totales'] = filtered_df_steelk['perforaTotal'].apply(Decimal) * filtered_df_steelk['espesor']
        
        perfo_filtered_df_steelk = filtered_df_steelk['perforaTotal'].sum()
        mm_filtered_df_steelk = filtered_df_steelk['mm totales'].sum()
        
        # Display Steelk metrics and visualizations
        display_summed_metrics_single_row("Steelk", perfo_filtered_df_steelk, mm_filtered_df_steelk)
        
        # Process and display Steelk charts
        grouped_df_steelk = process_and_display_charts(filtered_df_steelk, "Steelk")

    # --- Combined Analysis (Tiempo/Placa and Tiempo Seteo/Placa) ---
    if not (filtered_df_sabimet.empty and filtered_df_steelk.empty):
        process_combined_analysis(filtered_df_sabimet, filtered_df_steelk)

def process_and_display_charts(filtered_df, company_name):
    grouped_df = group_and_sum(filtered_df, ['pv', 'espesor'], 'placas').sort_values('placas',
                                                                                    ascending=False).reset_index(drop=True)
    
    columns_to_drop = [
        'Inicio', 'cantidadPerforacionesTotal', 'Terminado', 'cantidadPerforacionesPlacas',
        'kg', 'tipoMecanizado', 'progress_createdAt', 'origen', 'maquina', 'placas',
        'hora_reporte', 'tiempo', 'tiempo_seteo', 'espesor', 'negocio', 'perforaTotal',
        'Tiempo Proceso (min)'
    ]
    
    df_process_time = (filtered_df.drop_duplicates(subset=['Tiempo Proceso (min)'], keep='first')
                       .assign(Tiempo_Proceso_Dias=lambda x: (x['Tiempo Proceso (min)'] / (60 * 24)).round(2))
                       .drop(columns=columns_to_drop)
                       .groupby('pv', as_index=False)['Tiempo_Proceso_Dias'].sum()
                       .sort_values('Tiempo_Proceso_Dias', ascending=False)
                       .reset_index(drop=True))
    
    grouped_df = grouped_df.groupby(['pv', 'espesor'], as_index=False)['placas'].sum().sort_values('placas',
                                                                                                ascending=False).reset_index(drop=True)
    
    fig = bar_plot_with_hover_info(grouped_df)
    st.plotly_chart(fig)

    st.header(f"{company_name} Procesos")
    fig = bar_plot_with_hover_process(df_process_time)
    st.plotly_chart(fig)
    
    return grouped_df

def process_combined_analysis(filtered_df_sabimet, filtered_df_steelk):
    st.header("Tiempo/Placa Analysis")
    columns_to_drop = [
        'pv', 'Inicio', 'cantidadPerforacionesTotal', 'Terminado',
        'progress_createdAt', 'origen', 'placas', 'hora_reporte',
        'perforaTotal', 'Tiempo Proceso (min)'
    ]
    
    tiempo_seteo_sabimet = filter_and_drop_columns(filtered_df_sabimet, 'tiempo_seteo', 0, columns_to_drop) if not filtered_df_sabimet.empty else pd.DataFrame()
    tiempo_seteo_steelk = filter_and_drop_columns(filtered_df_steelk, 'tiempo_seteo', 0, columns_to_drop) if not filtered_df_steelk.empty else pd.DataFrame()
    
    if not (tiempo_seteo_sabimet.empty and tiempo_seteo_steelk.empty):
        group_columns = ['maquina', 'tipoMecanizado', 'espesor']
        avg_column = 'tiempo'
        
        if not tiempo_seteo_sabimet.empty:
            grouped_df_sabimet = group_and_average(tiempo_seteo_sabimet, group_columns, avg_column)
            tiempo_seteo_sabimet['negocio'] = 'Sabimet'
            
        if not tiempo_seteo_steelk.empty:
            grouped_df_steelk = group_and_average(tiempo_seteo_steelk, group_columns, avg_column)
            tiempo_seteo_steelk['negocio'] = 'Steelk'
        
        df_negocio = pd.concat([tiempo_seteo_sabimet, tiempo_seteo_steelk])
        
        fig = sunburst_plot(df_negocio, ['negocio'] + group_columns, 'Negocio', 'tiempo')
        st.plotly_chart(fig)

        st.header("Tiempo Seteo/Placa Analysis")
        fig = sunburst_plot(df_negocio, ['negocio'] + group_columns, 'Negocio', 'tiempo_seteo')
        st.plotly_chart(fig)
    else:
        st.error("⚠️ No tiempo/seteo data available for analysis")

if __name__ == "__main__":
    main()
