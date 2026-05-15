import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ページの基本設定
st.set_page_config(page_title="Cafe Positioning Map", layout="wide")

st.title("☕ カフェチェーン・ポジショニング分析（インタラクティブ版）")
st.write(
    "左のサイドバーから、比較したいブランドやキーワードを自由に選択して分析できます。"
)

# --- CSVの読み込み ---
try:
    brand_coords = pd.read_csv("brand_coords.csv", index_col=0)
    feature_coords = pd.read_csv("feature_coords.csv", index_col=0)
except FileNotFoundError:
    st.error(
        "CSVファイルが見つかりません。brand_coords.csv と feature_coords.csv を app_ca.py と同じフォルダに配置してください。"
    )
    st.stop()

# ==========================================
# 🚀 新機能：サイドバー（操作パネル）の作成
# ==========================================
st.sidebar.header("⚙️ 表示フィルター設定")

# デフォルトで「星乃珈琲」だけ外した状態のリストを作成（前回の考察を活かすため）
default_brands = [b for b in brand_coords.index if b != "星乃珈琲"]

# ブランドの複数選択メニュー
selected_brands = st.sidebar.multiselect(
    "🏢 比較するブランドを選択",
    options=brand_coords.index.tolist(),
    default=default_brands,  # 最初からチェックを入れておく項目
)

# キーワードの複数選択メニュー
selected_features = st.sidebar.multiselect(
    "🔑 表示するキーワードを選択",
    options=feature_coords.index.tolist(),
    default=feature_coords.index.tolist(),
)

# ユーザーが選択した項目だけでデータを絞り込む
filtered_brand_coords = brand_coords.loc[selected_brands]
filtered_feature_coords = feature_coords.loc[selected_features]

# --- プロット用の表を作成 ---
brand_df = pd.DataFrame(
    {
        "項目": filtered_brand_coords.index,
        "X": filtered_brand_coords["X"],
        "Y": filtered_brand_coords["Y"],
        "タイプ": "ブランド",
    }
)

feature_df = pd.DataFrame(
    {
        "項目": filtered_feature_coords.index,
        "X": filtered_feature_coords["X"],
        "Y": filtered_feature_coords["Y"],
        "タイプ": "特徴キーワード",
    }
)

# --- テキスト位置の個別調整（前回と同じ、重なり回避） ---
# キーワードの調整
feature_df["text_position"] = "bottom center"
for feature in ["個室あり", "スイーツ充実"]:
    if feature in feature_df["項目"].values:
        if feature == "個室あり":
            feature_df.loc[feature_df["項目"] == feature, "text_position"] = (
                "top center"
            )
        elif feature == "スイーツ充実":
            feature_df.loc[feature_df["項目"] == feature, "text_position"] = (
                "middle right"
            )

# ブランドの調整
brand_df["text_position"] = "top center"
for brand in ["スターバックス", "サンマルクカフェ"]:
    if brand in brand_df["項目"].values:
        if brand == "スターバックス":
            brand_df.loc[brand_df["項目"] == brand, "text_position"] = "middle left"
        elif brand == "サンマルクカフェ":
            brand_df.loc[brand_df["項目"] == brand, "text_position"] = "bottom center"


# --- Plotlyによる知覚マップの作成 ---
fig = go.Figure()

# 特徴キーワードのプロット
if not feature_df.empty:
    fig.add_trace(
        go.Scatter(
            x=feature_df["X"],
            y=feature_df["Y"],
            mode="markers+text",
            name="特徴キーワード",
            text=feature_df["項目"],
            textposition=feature_df["text_position"],
            textfont=dict(size=10, color="crimson"),
            marker=dict(color="crimson", size=10, symbol="diamond"),
            hoverinfo="text",
            hovertext=[f"<b>{row['項目']}</b>" for _, row in feature_df.iterrows()],
        )
    )

# ブランドのプロット
if not brand_df.empty:
    fig.add_trace(
        go.Scatter(
            x=brand_df["X"],
            y=brand_df["Y"],
            mode="markers+text",
            name="ブランド",
            text=brand_df["項目"],
            textposition=brand_df["text_position"],
            textfont=dict(size=11, color="royalblue", family="Arial Black"),
            marker=dict(color="royalblue", size=12, symbol="circle"),
            hoverinfo="text",
            hovertext=[f"<b>{row['項目']}</b>" for _, row in brand_df.iterrows()],
        )
    )

# グラフのレイアウト設定
fig.update_layout(
    title="コレスポンデンス分析による知覚マップ（バイプロット）",
    xaxis_title="第1次元：カジュアル⇔高級",
    yaxis_title="第2次元：食事⇔空間・ビジネス",
    showlegend=True,
    height=750,
    template="plotly_dark",
    hovermode="closest",
    xaxis=dict(
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="gray",
        gridcolor="rgb(50, 50, 50)",
    ),
    yaxis=dict(
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="gray",
        gridcolor="rgb(50, 50, 50)",
    ),
)

st.plotly_chart(fig, use_container_width=True)

# --- 解説セクション ---
st.header("🔍 ダッシュボードの活用方法")
st.write(
    "サイドバー（左側）のメニューから、特定の競合他社だけを残したり、不要なキーワードを消したりすることで、見たい市場の構造をよりクリアに分析できます。"
)
st.info(
    "※全体市場を俯瞰するために、座標軸自体は「全ブランド・全キーワード」で計算した市場構造（空間）を固定したまま、表示のON/OFFを切り替える仕様にしています。"
)
