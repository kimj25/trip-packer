#!/bin/bash
# Launch the Trip Packer Streamlit showcase.
set -e
cd "$(dirname "$0")"
streamlit run app.py
