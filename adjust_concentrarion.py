import streamlit as st

st.title("concentration tool")
solute = st.number_input("溶質(mg)", 0.000, 100000.000, 11.000)
solvent = st.number_input("溶媒(mg)", 0.000, 100000.000, 100.000)
wt = st.number_input("wt%", 0.00, 100.00, 0.1)


def wt_percent(solute, solvent):
    wt = 100 * solute / (solute + solvent)
    return wt


def solvent_w(wt, solute):
    solvent = (100 * solute / wt) - solute
    return solvent


def solute_w(wt, solvent):
    solute = (-wt * solvent) / (wt - 100)
    return solute


if st.button("wt%"):
    wt = wt_percent(solute, solvent)
    st.write("{}%".format(wt))

if st.button("溶質(mg)"):
    solute = solute_w(wt, solvent)
    st.write("{}mg".format(solute))

if st.button("溶媒(mg)"):
    solvent = solvent_w(wt, solute)
    st.write("{}mg".format(solvent))
