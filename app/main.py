import streamlit as st
from aws_client import list_ec2_instances
import os

st.title("CloudMind Analytics — Day 1 Test")

region = st.selectbox("Region", ["us-east-1", "ap-south-1", "us-west-2"])
if st.button("Fetch EC2 instances"):
    try:
        with st.spinner("Fetching EC2 instances..."):
            inst = list_ec2_instances(region)
            st.write(f"Found {len(inst)} instances in {region}")
            st.json(inst)
    except Exception as e:
        st.error(f"Error: {e}")
        st.text("Check AWS credentials, region and network.")
