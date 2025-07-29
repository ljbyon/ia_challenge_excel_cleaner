import streamlit as st
import pandas as pd
import io
import os

def main():
    st.title("Limpiador de Excel")
    st.write("Cargar archivo excel para remover columnas con sufijo '_xxx'")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        # Read the Excel file
        try:
            df = pd.read_excel(uploaded_file)
            
            # Display original dataframe info
            st.subheader("Tabla Original")
            st.write(f"Skus: {df.shape[0]}")
            st.write(f"Columnas: {df.shape[1]}")
            # Check if user wants to see the original data
            if st.checkbox("Mostrar tabla original"):
                st.dataframe(df)
            
            # Process the dataframe
            # Get columns that don't end with "_xxx"
            filtered_cols = [col for col in df.columns if not col.endswith("_xxx")]
            df_filtered = df[filtered_cols]
            
            # Replace "xxx" values with empty cells in remaining columns
            df_filtered = df_filtered.replace("xxx", "")
            
            # Display processed dataframe info
            st.subheader("Tabla procesada")
            st.write(f"Skus: {df_filtered.shape[0]}")
            st.write(f"Columnas: {df_filtered.shape[1]}")
            
            # Check if user wants to see the processed data
            if st.checkbox("Mostrar tabla procesada"):
                st.dataframe(df_filtered)
            
            # Create download button with original filename + "_limpio.xlsx"
            original_filename = uploaded_file.name
            filename_without_ext = os.path.splitext(original_filename)[0]
            output_filename = f"{filename_without_ext}_limpio.xlsx"
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, index=False, sheet_name='Sheet1')
            
            output.seek(0)
            
            st.download_button(
                label="Descargar Excel",
                data=output,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()