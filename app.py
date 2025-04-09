import streamlit as st
import pandas as pd
import io

def main():
    st.title("Excel Column Cleaner")
    st.write("Upload an Excel file to remove columns with '_xxx' suffix")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    
    if uploaded_file is not None:
        # Read the Excel file
        try:
            df = pd.read_excel(uploaded_file)
            
            # Display original dataframe info
            st.subheader("Original DataFrame")
            st.write(f"Shape: {df.shape}")
            st.write(f"Columns: {', '.join(df.columns.tolist())}")
            
            # Check if user wants to see the original data
            if st.checkbox("Show original data"):
                st.dataframe(df)
            
            # Process the dataframe
            # Get columns that don't end with "_xxx"
            filtered_cols = [col for col in df.columns if not col.endswith("_xxx")]
            df_filtered = df[filtered_cols]
            
            # Display processed dataframe info
            st.subheader("Processed DataFrame")
            st.write(f"Shape: {df_filtered.shape}")
            st.write(f"Columns: {', '.join(df_filtered.columns.tolist())}")
            
            # Check if user wants to see the processed data
            if st.checkbox("Show processed data"):
                st.dataframe(df_filtered)
            
            # Create download button
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, index=False, sheet_name='Sheet1')
            
            output.seek(0)
            
            st.download_button(
                label="Download processed Excel file",
                data=output,
                file_name="processed_excel.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()