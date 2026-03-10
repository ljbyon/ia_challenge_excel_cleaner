import streamlit as st
import pandas as pd
import io
import os

def find_problematic_cells(df):
    """
    Find cells that are blank or contain 'xxx'
    Returns a list of (row_index, column_name, value) tuples
    """
    problems = []
    
    for col in df.columns:
        # Check for blank cells (NaN or empty string)
        blank_mask = df[col].isna() | (df[col].astype(str).str.strip() == '')
        blank_indices = df[blank_mask].index.tolist()
        
        for idx in blank_indices:
            problems.append((idx, col, '[BLANK]'))
        
        # Check for 'xxx' values
        xxx_mask = df[col].astype(str).str.lower() == 'xxx'
        xxx_indices = df[xxx_mask].index.tolist()
        
        for idx in xxx_indices:
            problems.append((idx, col, 'xxx'))
    
    return problems

def display_problems(problems, df):
    """Display problematic cells in a user-friendly format"""
    if not problems:
        return
    
    st.error(f"⚠️ Se encontraron {len(problems)} celdas problemáticas (vacías o con 'xxx')")
    
    # Create a dataframe for display
    problem_data = []
    for row_idx, col_name, value in problems:
        # Get SKU or identifier if exists (assuming first column might be SKU/ID)
        row_identifier = df.iloc[row_idx, 0] if len(df.columns) > 0 else row_idx
        problem_data.append({
            'Fila': row_idx + 2,  # +2 because Excel is 1-indexed and has header
            'SKU/ID': row_identifier,
            'Columna': col_name,
            'Problema': value
        })
    
    problem_df = pd.DataFrame(problem_data)
    st.dataframe(problem_df, use_container_width=True, height=300)
    
    # Download button for problems report
    problems_csv = problem_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar reporte de problemas (CSV)",
        data=problems_csv,
        file_name="problemas_validacion.csv",
        mime="text/csv"
    )

def main():
    st.title("🧹 Limpiador de Excel - Dual Output")
    st.write("Genera 2 archivos Excel: uno para Akeneo y otro para archivo")
    
    uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # Read the Excel file
            with st.spinner("Cargando archivo..."):
                #df_original = pd.read_excel(uploaded_file)
                df_original = pd.read_excel(uploaded_file, dtype={"sku": str})
            
            # Validate file has data
            if df_original.empty:
                st.warning("⚠️ El archivo está vacío")
                return
            
            # Display original dataframe info
            st.subheader("📊 Archivo Original")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Filas (SKUs)", df_original.shape[0])
            with col2:
                st.metric("Columnas", df_original.shape[1])
            
            if st.checkbox("👁️ Mostrar tabla original"):
                st.dataframe(df_original, use_container_width=True)
            
            st.divider()
            
            # Step 1: Remove columns ending with _xxx
            original_cols = df_original.columns.tolist()
            filtered_cols = [col for col in original_cols if not col.endswith("_xxx")]
            removed_cols = [col for col in original_cols if col.endswith("_xxx")]
            
            df_base = df_original[filtered_cols].copy()
            
            st.info(f"✓ Columnas con sufijo '_xxx' removidas: {len(removed_cols)}")
            if removed_cols and st.checkbox("Ver columnas removidas"):
                st.write(", ".join(removed_cols))
            
            # Step 2: Validation - Check for blank or 'xxx' cells
            st.subheader("🔍 Validación de Datos")
            
            with st.spinner("Validando celdas..."):
                problems = find_problematic_cells(df_base)
            
            if problems:
                st.warning("⚠️ Validación falló - Se encontraron problemas")
                display_problems(problems, df_base)
                st.info("💡 Corrige estos problemas en el archivo original y vuelve a cargarlo")
                return
            else:
                st.success("✅ Validación exitosa - No se encontraron celdas vacías o con 'xxx'")
            
            st.divider()
            
            # ========== EXCEL 1: AKENEO ==========
            st.subheader("📤 Excel 1: Para Akeneo")
            
            df_akeneo = df_base.copy()
            
            # Convert all string columns to lowercase for matching
            # Then replace 'postergado' with empty string
            postergado_count = 0
            for col in df_akeneo.columns:
                # Create lowercase version for comparison
                lower_series = df_akeneo[col].astype(str).str.lower()
                postergado_mask = lower_series == 'postergado'
                postergado_count += postergado_mask.sum()
                # Replace with empty string
                df_akeneo.loc[postergado_mask, col] = ''
            
            st.success(f"✅ Valores 'postergado' limpiados: {postergado_count}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Filas", df_akeneo.shape[0])
            with col2:
                st.metric("Columnas", df_akeneo.shape[1])
            
            if st.checkbox("👁️ Mostrar Excel Akeneo"):
                st.dataframe(df_akeneo, use_container_width=True)
            
            # Create download button for Akeneo
            original_filename = uploaded_file.name
            filename_without_ext = os.path.splitext(original_filename)[0]
            akeneo_filename = f"{filename_without_ext}_limpio.xlsx"
            
            output_akeneo = io.BytesIO()
            # with pd.ExcelWriter(output_akeneo, engine='xlsxwriter') as writer:
            #     df_akeneo.to_excel(writer, index=False, sheet_name='Sheet1')


            with pd.ExcelWriter(output_akeneo, engine='xlsxwriter',
                                options={'strings_to_numbers': False}) as writer:
                df_akeneo.to_excel(writer, index=False, sheet_name='Sheet1')


            output_akeneo.seek(0)
            
            st.download_button(
                label="⬇️ Descargar Excel Akeneo",
                data=output_akeneo,
                file_name=akeneo_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
            
            st.divider()
            
            # ========== EXCEL 2: ARCHIVE ==========
            st.subheader("📁 Excel 2: Para Archivo")
            
            df_archive = df_base.copy()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Filas", df_archive.shape[0])
            with col2:
                st.metric("Columnas", df_archive.shape[1])
            
            if st.checkbox("👁️ Mostrar Excel Archivo"):
                st.dataframe(df_archive, use_container_width=True)
            
            # Create download button for Archive
            archive_filename = f"{filename_without_ext}_archivo.xlsx"
            
            output_archive = io.BytesIO()
            # with pd.ExcelWriter(output_archive, engine='xlsxwriter') as writer:
            #     df_archive.to_excel(writer, index=False, sheet_name='Sheet1')

            with pd.ExcelWriter(output_archive, engine='xlsxwriter',
                                options={'strings_to_numbers': False}) as writer:
                df_archive.to_excel(writer, index=False, sheet_name='Sheet1')


            output_archive.seek(0)
            
            st.download_button(
                label="⬇️ Descargar Excel Archivo",
                data=output_archive,
                file_name=archive_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="secondary"
            )
            
            st.divider()
            st.success("🎉 Ambos archivos generados exitosamente")
            
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
            import traceback
            with st.expander("Ver detalles del error"):
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()