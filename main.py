import streamlit as st
import numpy as np

col1, col2, col3 = st.columns([1, 1, 3])
data = np.random.randn(10, 1)

col1.subheader("A wide column with a chart")
col2.write(data)

col2.subheader("A narrow column with the data")
col2.write(data)

col3.subheader("A wide column with a chart")
col3.line_chart(data)
