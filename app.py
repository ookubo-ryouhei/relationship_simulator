import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# --- 【修正ポイント】日本語フォントの設定 ---
# Windows標準の「MS Gothic」を指定することで、追加ライブラリなしで日本語表示を可能にします
plt.rcParams['font.family'] = 'MS Gothic' 

# --- ページ設定 ---
st.set_page_config(page_title="散布図・相関関係可視化ツール", layout="wide")

# タイトル
st.title("📊 散布図・相関関係可視化ツール")
st.markdown("""
このツールでは、2つのデータの関係性（相関）を散布図と相関係数で確認できます。
左のメニューから分析したいテーマを選んでみましょう！
""")

# --- サイドバー：設定パネル ---
st.sidebar.header("🕹️ 操作パネル")

dataset_type = st.sidebar.radio(
    "分析するデータを選んでください",
    (
        "📱 スマホ時間とテスト点数 (負の相関)", 
        "👟 身長と靴のサイズ (正の相関)", 
        "🎲 出席番号とテスト点数 (無相関)"
    )
)

st.sidebar.divider()
num_students = st.sidebar.slider("生徒数（データ件数）", min_value=10, max_value=200, value=50, step=10)
generate_btn = st.sidebar.button("🔄 データを再生成")

# --- データ生成関数 ---
@st.cache_data
def generate_correlation_data(n, dtype):
    # ボタンが押されたらシードを変えるための工夫
    if 'regen_trigger' not in st.session_state:
        st.session_state['regen_trigger'] = 0
    np.random.seed(42 + st.session_state['regen_trigger'])

    df = pd.DataFrame({'生徒ID': range(1, n + 1)})

    if dtype == "📱 スマホ時間とテスト点数 (負の相関)":
        usage_time = np.round(np.random.uniform(0.5, 6.0, n), 1)
        scores = 100 - (usage_time * 12) + np.random.normal(0, 8, n)
        df['スマホ利用時間(時間)'] = usage_time
        df['テストの点数'] = np.clip(scores, 0, 100).astype(int)

    elif dtype == "👟 身長と靴のサイズ (正の相関)":
        heights = np.round(np.random.normal(165, 8, n), 1)
        shoes = heights * 0.15 + np.random.normal(0, 1.0, n)
        df['身長(cm)'] = heights
        df['靴のサイズ(cm)'] = np.round(shoes * 2) / 2

    elif dtype == "🎲 出席番号とテスト点数 (無相関)":
        scores = np.random.normal(60, 15, n)
        df['出席番号'] = range(1, n + 1)
        df['テストの点数'] = np.clip(scores, 0, 100).astype(int)

    return df

if generate_btn:
    st.session_state['regen_trigger'] = st.session_state.get('regen_trigger', 0) + 1

df = generate_correlation_data(num_students, dataset_type)

# --- データ分析・可視化エリア ---
st.header(f"テーマ: {dataset_type}")

col_data1, col_data2 = st.columns(2)
with col_data1:
    st.subheader("📋 データプレビュー")
    st.dataframe(df.head(), use_container_width=True)

with col_data2:
    st.subheader("🔢 基本統計量")
    st.dataframe(df.describe(), use_container_width=True)

st.subheader("📈 散布図と相関関係の分析")

numeric_cols = [col for col in df.columns if col != '生徒ID']

if len(numeric_cols) >= 2:
    x_axis = numeric_cols[0]
    y_axis = numeric_cols[1]

    col_plot, col_corr = st.columns([2, 1])
    
    with col_plot:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax, s=100, alpha=0.7)
        
        show_reg = st.checkbox("回帰直線（傾向線）を表示する", value=True)
        if show_reg:
            sns.regplot(data=df, x=x_axis, y=y_axis, ax=ax, scatter=False, color='red', line_kws={'linestyle':'--'})
        
        ax.set_title(f"{x_axis} と {y_axis} の散布図", fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

    with col_corr:
        st.write("### 相関係数 ($r$)")
        correlation = df[x_axis].corr(df[y_axis])
        st.metric(label=f"{x_axis} vs {y_axis}", value=f"{correlation:.3f}")

        st.write("#### 判定:")
        r_abs = abs(correlation)
        if r_abs >= 0.7:
            st.success("✅ **強い相関**があります。")
        elif r_abs >= 0.4:
            st.info("⚠️ **中程度の相関**があります。")
        elif r_abs >= 0.2:
            st.warning("🧐 **弱い相関**があります。")
        else:
            st.error("✖️ **ほとんど相関**がありません。")

        st.markdown("""
        ---
        **【情報Ⅰのポイント】**
        相関があるからといって因果関係があるとは限りません。
        """)
