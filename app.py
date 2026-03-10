import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conciliação TEF", layout="wide")

st.title("Conciliação de Cartões")

st.write("Envie os três arquivos para conciliar:")

tef_file = st.file_uploader("1️⃣ Relatório TEF", type=["csv"])
maq_file = st.file_uploader("2️⃣ Relatório da Maquineta", type=["csv","xlsx"])
ext_file = st.file_uploader("3️⃣ Extrato Bancário", type=["csv","xlsx"])


# ---------------------------
# LEITURA DO TEF
# ---------------------------

def carregar_tef(file):

    df = pd.read_csv(
        file,
        sep=";",
        encoding="latin1",
        skiprows=4
    )

    df.columns = df.columns.str.replace('"', '').str.strip()

    df["Valor"] = (
        df["Valor"]
        .astype(str)
        .str.replace(",", ".")
        .astype(float)
    )

    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)

    df = df[df["Estado Transação"] == "Efetuada PDV"]

    return df


# ---------------------------
# LEITURA MAQUINETA
# ---------------------------

def carregar_maquineta(file):

    if file.name.endswith("xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    return df


# ---------------------------
# LEITURA EXTRATO
# ---------------------------

def carregar_extrato(file):

    if file.name.endswith("xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    return df


# ---------------------------
# PROCESSAMENTO
# ---------------------------

if tef_file:

    tef = carregar_tef(tef_file)

    st.subheader("TEF carregado")

    st.dataframe(tef, use_container_width=True)

    resumo_tef = (
        tef.groupby(["Data","Tipo Produto"])["Valor"]
        .sum()
        .reset_index()
    )

    st.subheader("Resumo TEF")

    st.dataframe(resumo_tef)


    if maq_file:

        maq = carregar_maquineta(maq_file)

        st.subheader("Relatório Maquineta")

        st.dataframe(maq)

    if ext_file:

        ext = carregar_extrato(ext_file)

        st.subheader("Extrato Bancário")

        st.dataframe(ext)


    # ---------------------------
    # RESUMO GERAL
    # ---------------------------

    st.subheader("Totais TEF")

    total_tef = tef["Valor"].sum()

    st.metric("Total TEF", f"R$ {total_tef:,.2f}")
