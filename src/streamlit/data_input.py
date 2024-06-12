import pandas as pd
import os
import streamlit as st


def streamlit_data_input(default_data_path):
    if "data_loaded" not in st.session_state:  # Check if data has been loaded
        st.session_state.data_loaded = False  # Initialize the flag

    if not st.session_state.data_loaded:
        st.markdown("### Data Upload")
        st.markdown(
            "Please upload the ```.csv``` file containing all of the transactions you want to analyze."
        )
        fl = st.file_uploader("Upload a file", type=["csv", "xlsx", "html", "h5"])
        if fl is not None:
            st.write(fl.name)
            if fl.endswith(".csv"):
                df = pd.read_csv(fl)
                df.columns = pd.MultiIndex.from_tuples(
                    [tuple(c.split(".")) for c in df.columns]
                )
            elif fl.endswith(".h5"):
                df = pd.read_hdf(fl)
            df = pd.read_csv(fl)
            st.session_state["data"] = df  # Save data to session state
            st.session_state.data_loaded = True  # Set the flag to True
        else:
            if default_data_path.endswith(".csv"):
                df = pd.read_csv(default_data_path)
                print("\nHello World\n  ", df.columns)
                df.columns = pd.MultiIndex.from_tuples(
                    [tuple(c.split(".")) for c in df.columns]
                )
            elif default_data_path.endswith(".h5"):
                df = pd.read_hdf(default_data_path)
            st.session_state["data"] = df  # Optionally, save this also to session state
            st.session_state.data_loaded = True  # Set the flag to True
    else:
        df = st.session_state["data"]

    return df
