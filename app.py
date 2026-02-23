import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Crypto Tracker Dashboard", layout="wide", page_icon="🪙")
st.title("🪙 Crypto Data Interactive Dashboard")
st.markdown("วิเคราะห์และแสดงผลข้อมูลคริปโตเคอร์เรนซี")

# 1. ส่วนของการอัปโหลดไฟล์ CSV บน Dashboard
st.sidebar.header("📂 อัปโหลดไฟล์ข้อมูล")
uploaded_file = st.sidebar.file_uploader("อัปโหลดไฟล์ Crypto CSV ที่โหลดจาก Kaggle", type=['csv'])

if uploaded_file is not None:
    # อ่านไฟล์ CSV
    df = pd.read_csv(uploaded_file)
    
    # พยายามแปลงคอลัมน์วันที่อัตโนมัติ (ถ้ามี)
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    if date_cols:
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='ignore')

    st.sidebar.header("🔍 Filter ข้อมูลแบบเฉพาะเจาะจง")
    
    # ค้นหาคอลัมน์ที่เป็นชื่อเหรียญอัตโนมัติเพื่อใช้ทำ Filter
    coin_col = None
    for col in ['Name', 'Symbol', 'Coin', 'Asset', 'Currency']:
        if col in df.columns:
            coin_col = col
            break
            
    filtered_df = df.copy()
    
    # Filter 1: เลือกชื่อเหรียญ
    if coin_col:
        coins = df[coin_col].unique()
        selected_coins = st.sidebar.multiselect(f"เลือก {coin_col}:", coins, default=coins[:5] if len(coins) > 5 else coins)
        filtered_df = filtered_df[filtered_df[coin_col].isin(selected_coins)]
        
    # Filter 2: กรองช่วงของตัวเลข (เช่น ราคา Close, Volume)
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(num_cols) > 0:
        target_num_col = st.sidebar.selectbox("เลือกตัวแปรสำหรับกำหนดช่วงข้อมูล:", num_cols)
        min_val = float(df[target_num_col].min())
        max_val = float(df[target_num_col].max())
        selected_range = st.sidebar.slider(f"ช่วงของ {target_num_col}", min_val, max_val, (min_val, max_val))
        filtered_df = filtered_df[(filtered_df[target_num_col] >= selected_range[0]) & (filtered_df[target_num_col] <= selected_range[1])]

    # แสดงสถิติเบื้องต้น
    st.header("📈 สถิติสำคัญ (จากข้อมูลที่ Filter)")
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนรายการทั้งหมด", f"{len(filtered_df):,}")
    
    if len(num_cols) > 0:
        avg_val = filtered_df[num_cols[0]].mean()
        col2.metric(f"ค่าเฉลี่ย {num_cols[0]}", f"{avg_val:,.2f}")
        max_val = filtered_df[num_cols[0]].max()
        col3.metric(f"ค่าสูงสุด {num_cols[0]}", f"{max_val:,.2f}")

    st.divider()

    # กราฟพร้อม Data Labels (ทำตามโจทย์เป๊ะๆ)
    st.header("📊 กราฟวิเคราะห์ข้อมูลคริปโต")
    
    tab1, tab2 = st.tabs(["กราฟแท่ง (เปรียบเทียบข้อมูล)", "กราฟเส้น (แนวโน้มเวลา)"])
    
    with tab1:
        # มีการใช้ Chart Data Labels เพื่อแสดงตัวเลขบนแท่งกราฟ
        if coin_col and len(num_cols) > 0:
            bar_data = filtered_df.groupby(coin_col)[num_cols[0]].mean().reset_index()
            bar_data = bar_data.sort_values(by=num_cols[0], ascending=False).head(10)
            
            fig_bar = px.bar(
                bar_data, 
                x=coin_col, 
                y=num_cols[0],
                title=f"เปรียบเทียบค่าเฉลี่ย {num_cols[0]} ของแต่ละเหรียญ",
                text_auto='.2s' # เปิดใช้งาน Data Labels แบบย่อตัวเลข
            )
            fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("ระบบไม่พบคอลัมน์ที่เหมาะสมสำหรับสร้างกราฟแท่ง")

    with tab2:
        # แสดงแนวโน้มหากมีคอลัมน์วันที่
        if date_cols and len(num_cols) > 0:
            color_arg = coin_col if coin_col in filtered_df.columns else None
            fig_line = px.line(
                filtered_df, 
                x=date_cols[0], 
                y=num_cols[0],
                color=color_arg,
                title=f"แนวโน้ม {num_cols[0]} ตามช่วงเวลา"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("ระบบไม่พบคอลัมน์วันที่สำหรับสร้างกราฟเส้น")

    st.divider()

    # แสดงรายละเอียดข้อมูลทั้งหมด (Raw Data)
    st.header("📋 รายละเอียดข้อมูลทั้งหมด")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("รอรับไฟล์... กรุณาดาวน์โหลดไฟล์ .CSV ของคุณจาก Kaggle แล้วอัปโหลดที่แถบด้านซ้ายมือครับ")
