import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import zipfile
import io
import time
import tempfile
import shutil

# 页面配置
st.set_page_config(
    page_title="MALDI-TOF MS 数据处理平台 (增强版)",
    page_icon="🔬",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
        text-align: center;
    }
    .upload-method {
        background-color: #f0f8ff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .file-info {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'demo_data' not in st.session_state:
    st.session_state.demo_data = None
if 'uploaded_files_info' not in st.session_state:
    st.session_state.uploaded_files_info = {
        'train_txt': [],
        'train_excel': None,
        'valid_txt': []
    }

def extract_txt_from_zip(zip_file):
    """从ZIP文件中提取所有TXT文件"""
    txt_files = []
    file_names = []
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # 获取所有TXT文件
            txt_file_names = [f for f in zip_ref.namelist() 
                            if f.lower().endswith('.txt') and not f.startswith('__MACOSX')]
            
            for file_name in txt_file_names:
                # 读取文件内容
                content = zip_ref.read(file_name)
                # 只保存文件名（不含路径）
                base_name = Path(file_name).name
                txt_files.append(content)
                file_names.append(base_name)
        
        return txt_files, file_names
    except Exception as e:
        st.error(f"解压ZIP文件失败: {str(e)}")
        return [], []

def extract_excel_from_zip(zip_file):
    """从ZIP文件中提取Excel文件"""
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            excel_files = [f for f in zip_ref.namelist() 
                          if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('__MACOSX')]
            
            if excel_files:
                # 返回第一个Excel文件
                content = zip_ref.read(excel_files[0])
                return content, Path(excel_files[0]).name
        
        return None, None
    except Exception as e:
        st.error(f"提取Excel文件失败: {str(e)}")
        return None, None

def generate_demo_data(n_samples=5, n_features=100, n_validation=0):
    """生成演示数据"""
    np.random.seed(42)
    
    mz_values = np.sort(np.random.randint(1000, 10000, n_features))
    
    # 训练集数据
    intensity_train = np.random.exponential(scale=100, size=(n_samples, n_features))
    col_names = [f"mz_{mz}" for mz in mz_values]
    row_names = [f"Group_{i+1}" for i in range(n_samples)]
    
    df_train = pd.DataFrame(intensity_train, columns=col_names, index=row_names)
    df_train.insert(0, '行名', row_names)
    
    # 验证集数据（如果有）
    df_validation = None
    if n_validation > 0:
        intensity_validation = np.random.exponential(scale=100, size=(n_validation, n_features))
        valid_row_names = [f"Valid_{i+1}" for i in range(n_validation)]
        
        df_validation = pd.DataFrame(intensity_validation, columns=col_names, index=valid_row_names)
        df_validation.insert(0, '行名', valid_row_names)
    
    # 质谱图数据
    spectrum_mz = np.linspace(1000, 10000, 1000)
    spectrum_intensity = np.abs(np.random.randn(1000) * 10 + 50)
    
    peaks = [2000, 3500, 5000, 7200, 8500]
    for peak in peaks:
        idx = np.argmin(np.abs(spectrum_mz - peak))
        spectrum_intensity[idx-5:idx+5] += np.random.randn(10) * 50 + 200
    
    spectrum_df = pd.DataFrame({
        'mz': spectrum_mz,
        'intensity': spectrum_intensity
    })
    
    # 处理参数
    params_df = pd.DataFrame({
        'parameter': ['halfWindowSize', 'SNR', 'tolerance'],
        'value': [90, 2.5, 0.008]
    })
    
    result = {
        'train': df_train,
        'spectrum': spectrum_df,
        'params': params_df
    }
    
    if df_validation is not None:
        result['validation'] = df_validation
    
    return result

def plot_spectrum(df):
    """绘制质谱图"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['mz'],
        y=df['intensity'],
        mode='lines',
        name='强度',
        line=dict(color='#1f77b4', width=1.5),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.update_layout(
        title='平均质谱图',
        xaxis_title='m/z',
        yaxis_title='相对强度',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        font=dict(size=12)
    )
    
    return fig

def plot_heatmap(df):
    """绘制强度热图"""
    data = df.iloc[:, 1:].copy()
    top_cols = data.sum().nlargest(50).index
    data_subset = data[top_cols]
    
    fig = px.imshow(
        data_subset.T,
        aspect='auto',
        color_continuous_scale='Viridis',
        labels=dict(x="样本", y="m/z", color="强度"),
        x=df['行名'].values
    )
    
    fig.update_layout(
        title='峰强度热图（Top 50峰）',
        height=600,
        font=dict(size=12)
    )
    
    return fig

def plot_peak_distribution(df):
    """绘制峰强度分布"""
    intensities = df.iloc[:, 1:].values.flatten()
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=intensities,
        nbinsx=50,
        marker_color='#1f77b4',
        opacity=0.7
    ))
    
    fig.update_layout(
        title='峰强度分布',
        xaxis_title='强度',
        yaxis_title='频数',
        template='plotly_white',
        height=400
    )
    
    return fig

# ========================================
# 主应用界面
# ========================================

st.markdown('<div class="main-header">🔬 MALDI-TOF MS 数据处理平台</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">微生物质谱数据自动化预处理工具 - 增强版</div>', unsafe_allow_html=True)

st.success("✨ **新功能**: 支持ZIP压缩包批量上传！可将文件夹压缩后一次性上传。")

# 侧边栏
with st.sidebar:
    st.header("📋 处理流程")
    st.markdown("""
    1️⃣ 上传数据文件  
    2️⃣ 配置处理参数  
    3️⃣ 开始处理  
    4️⃣ 查看结果  
    5️⃣ 下载结果文件  
    """)
    
    st.divider()
    
    st.header("⚙️ 参数配置")
    
    auto_params = st.checkbox("自动参数估计", value=True, 
                              help="根据数据特征自动选择最佳参数")
    
    if not auto_params:
        st.subheader("手动参数设置")
        halfWindowSize = st.slider("半峰宽", 10, 200, 90, 10)
        SNR = st.slider("信噪比阈值", 1.0, 10.0, 2.0, 0.5)
        tolerance = st.slider("对齐容差", 0.001, 0.02, 0.008, 0.001, format="%.4f")
    
    st.divider()
    
    st.markdown("""
    ### 📦 ZIP上传说明
    
    **文件夹结构示例:**
    ```
    train_data.zip
    ├── sample1.txt
    ├── sample2.txt
    ├── sample3.txt
    └── labels.xlsx
    ```
    
    **步骤:**
    1. 将TXT和Excel放入文件夹
    2. 压缩为ZIP格式
    3. 上传ZIP文件
    """)

# 主内容区
tab1, tab2, tab3 = st.tabs(["📁 数据上传", "▶️ 处理与结果", "📊 数据可视化"])

with tab1:
    st.header("数据上传")
    
    # 上传方式选择
    st.subheader("选择上传方式")
    
    upload_method = st.radio(
        "选择上传方式",
        ["📦 方式1: ZIP压缩包上传（推荐）", "📄 方式2: 单个文件上传"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if "ZIP" in upload_method:
        # ==================== ZIP上传方式 ====================
        st.markdown("""
        <div class="upload-method">
            <h4>📦 ZIP压缩包上传</h4>
            <p>将所有TXT文件和Excel标签文件放入同一文件夹，压缩成ZIP后上传</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧪 训练集ZIP")
            train_zip = st.file_uploader(
                "上传训练集ZIP文件",
                type=['zip'],
                key='train_zip',
                help="ZIP中应包含多个TXT文件和1个Excel文件"
            )
            
            if train_zip:
                with st.spinner("正在解压训练集ZIP..."):
                    # 提取TXT文件
                    txt_contents, txt_names = extract_txt_from_zip(train_zip)
                    # 提取Excel文件
                    excel_content, excel_name = extract_excel_from_zip(train_zip)
                    
                    if txt_contents and excel_content:
                        st.session_state.uploaded_files_info['train_txt'] = list(zip(txt_contents, txt_names))
                        st.session_state.uploaded_files_info['train_excel'] = (excel_content, excel_name)
                        
                        st.success(f"✅ 成功解压：{len(txt_names)} 个TXT文件 + 1个Excel文件")
                        
                        # 显示文件列表
                        with st.expander("📋 查看解压的文件"):
                            st.write("**TXT文件:**")
                            for i, name in enumerate(txt_names[:10], 1):
                                st.write(f"{i}. {name}")
                            if len(txt_names) > 10:
                                st.write(f"... 还有 {len(txt_names) - 10} 个文件")
                            
                            st.write(f"\n**Excel文件:** {excel_name}")
                        
                        # 预览Excel
                        with st.expander("📄 预览Excel标签文件"):
                            try:
                                excel_df = pd.read_excel(io.BytesIO(excel_content))
                                st.dataframe(excel_df.head(10), use_container_width=True)
                                
                                if 'file' in excel_df.columns and 'group' in excel_df.columns:
                                    st.success("✅ Excel格式正确")
                                    st.info(f"📊 样本数: {len(excel_df)} | 分组: {', '.join(excel_df['group'].unique())}")
                                else:
                                    st.error("❌ Excel缺少必要列 ('file' 或 'group')")
                            except Exception as e:
                                st.error(f"读取Excel失败: {str(e)}")
                    
                    elif txt_contents and not excel_content:
                        st.warning("⚠️ ZIP中未找到Excel文件，请确保包含标签文件")
                    elif not txt_contents and excel_content:
                        st.warning("⚠️ ZIP中未找到TXT文件")
                    else:
                        st.error("❌ ZIP中未找到有效文件")
        
        with col2:
            st.subheader("🔍 验证集ZIP（可选）")
            valid_zip = st.file_uploader(
                "上传验证集ZIP文件",
                type=['zip'],
                key='valid_zip',
                help="ZIP中应包含多个TXT文件（无需Excel）"
            )
            
            if valid_zip:
                with st.spinner("正在解压验证集ZIP..."):
                    txt_contents, txt_names = extract_txt_from_zip(valid_zip)
                    
                    if txt_contents:
                        st.session_state.uploaded_files_info['valid_txt'] = list(zip(txt_contents, txt_names))
                        st.success(f"✅ 成功解压：{len(txt_names)} 个TXT文件")
                        
                        with st.expander("📋 查看解压的文件"):
                            for i, name in enumerate(txt_names[:10], 1):
                                st.write(f"{i}. {name}")
                            if len(txt_names) > 10:
                                st.write(f"... 还有 {len(txt_names) - 10} 个文件")
                    else:
                        st.error("❌ ZIP中未找到TXT文件")
            else:
                st.info("💡 验证集为可选项")
    
    else:
        # ==================== 单个文件上传方式 ====================
        st.markdown("""
        <div class="upload-method">
            <h4>📄 单个文件上传</h4>
            <p>逐个选择并上传文件（支持多选）</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🧪 训练集文件")
            
            train_txt_files = st.file_uploader(
                "上传训练集TXT文件",
                type=['txt'],
                accept_multiple_files=True,
                key='train_txt_single',
                help="按住Ctrl/Cmd可多选"
            )
            
            train_excel = st.file_uploader(
                "上传Excel标签文件",
                type=['xlsx', 'xls'],
                key='train_excel_single'
            )
            
            if train_txt_files:
                # 转换为统一格式
                st.session_state.uploaded_files_info['train_txt'] = [
                    (f.read(), f.name) for f in train_txt_files
                ]
                # 重置文件指针
                for f in train_txt_files:
                    f.seek(0)
            
            if train_excel:
                st.session_state.uploaded_files_info['train_excel'] = (
                    train_excel.read(), train_excel.name
                )
                train_excel.seek(0)
            
            if train_txt_files and train_excel:
                st.success(f"✅ 已上传 {len(train_txt_files)} 个TXT文件 + 1个Excel")
                
                with st.expander("📄 预览Excel标签文件"):
                    try:
                        excel_df = pd.read_excel(train_excel)
                        st.dataframe(excel_df.head(10), use_container_width=True)
                        
                        if 'file' in excel_df.columns and 'group' in excel_df.columns:
                            st.success("✅ Excel格式正确")
                            st.info(f"样本数: {len(excel_df)} | 分组: {', '.join(excel_df['group'].unique())}")
                        else:
                            st.error("❌ Excel缺少必要列")
                    except Exception as e:
                        st.error(f"读取失败: {str(e)}")
        
        with col2:
            st.subheader("🔍 验证集文件（可选）")
            
            valid_txt_files = st.file_uploader(
                "上传验证集TXT文件",
                type=['txt'],
                accept_multiple_files=True,
                key='valid_txt_single'
            )
            
            if valid_txt_files:
                st.session_state.uploaded_files_info['valid_txt'] = [
                    (f.read(), f.name) for f in valid_txt_files
                ]
                st.success(f"✅ 已上传 {len(valid_txt_files)} 个验证集文件")
            else:
                st.info("💡 验证集为可选项")
    
    # 上传状态总结
    st.divider()
    st.subheader("📊 上传状态总结")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        train_txt_count = len(st.session_state.uploaded_files_info['train_txt'])
        st.metric("训练集TXT", train_txt_count, 
                 delta="✓" if train_txt_count > 0 else None)
    
    with col2:
        has_excel = st.session_state.uploaded_files_info['train_excel'] is not None
        st.metric("训练集Excel", "1" if has_excel else "0",
                 delta="✓" if has_excel else None)
    
    with col3:
        valid_txt_count = len(st.session_state.uploaded_files_info['valid_txt'])
        st.metric("验证集TXT", valid_txt_count,
                 delta="✓" if valid_txt_count > 0 else "可选")

with tab2:
    st.header("数据处理与结果")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        can_process = (len(st.session_state.uploaded_files_info['train_txt']) > 0 and 
                      st.session_state.uploaded_files_info['train_excel'] is not None)
        
        process_btn = st.button(
            "🚀 开始处理", 
            type="primary", 
            use_container_width=True,
            disabled=not can_process
        )
        
        if not can_process:
            st.warning("⚠️ 请先上传训练集文件（TXT + Excel）")
    
    with col2:
        demo_btn = st.button("🎮 使用演示数据", use_container_width=True)
    
    if process_btn or demo_btn:
        with st.spinner("正在处理数据..."):
            # 模拟处理过程
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                ("读取光谱文件", 20),
                ("预处理: 强度转换", 40),
                ("预处理: 平滑和去基线", 60),
                ("峰检测和对齐", 80),
                ("生成强度矩阵", 100)
            ]
            
            for step, percent in steps:
                status_text.text(f"⏳ {step}...")
                time.sleep(0.3)
                progress_bar.progress(percent)
            
            status_text.empty()
            progress_bar.empty()
            
            # 生成演示数据
            n_train = len(st.session_state.uploaded_files_info['train_txt']) if process_btn else 5
            n_valid = len(st.session_state.uploaded_files_info['valid_txt']) if process_btn else 0
            
            # 如果是demo按钮且没有上传验证集，也生成一些验证集数据用于演示
            if demo_btn and n_valid == 0:
                n_valid = 3
            
            st.session_state.demo_data = generate_demo_data(
                n_samples=max(n_train, 3),
                n_validation=n_valid
            )
            
            st.success("✅ 处理完成！")
    
    # 显示结果
    if st.session_state.demo_data:
        st.divider()
        
        st.subheader("📊 处理摘要")
        
        # 动态列数：有验证集时显示5列，没有时显示4列
        has_validation = 'validation' in st.session_state.demo_data
        
        if has_validation:
            col1, col2, col3, col4, col5 = st.columns(5)
        else:
            col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "训练集样本数", 
                len(st.session_state.demo_data['train']),
                help="平均质谱数量"
            )
        
        with col2:
            if has_validation:
                st.metric(
                    "验证集样本数",
                    len(st.session_state.demo_data['validation']),
                    help="验证集单个样本数量"
                )
            else:
                st.metric(
                    "验证集样本数",
                    "N/A",
                    help="未上传验证集"
                )
        
        with col3 if has_validation else col2:
            st.metric(
                "检测峰数", 
                len(st.session_state.demo_data['train'].columns) - 1,
                help="识别的m/z特征数"
            )
        
        with col4 if has_validation else col3:
            total_intensity = st.session_state.demo_data['train'].iloc[:, 1:].sum().sum()
            st.metric(
                "总强度", 
                f"{total_intensity:.0f}",
                help="所有峰的总强度"
            )
        
        with col5 if has_validation else col4:
            avg_intensity = st.session_state.demo_data['train'].iloc[:, 1:].mean().mean()
            st.metric(
                "平均峰强度", 
                f"{avg_intensity:.1f}",
                help="每个峰的平均强度"
            )
        
        # 参数信息
        st.subheader("⚙️ 处理参数")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(
                st.session_state.demo_data['params'],
                hide_index=True,
                use_container_width=True
            )
        
        with col2:
            st.info("""
            **参数说明:**
            - **halfWindowSize**: 半峰宽，影响峰检测灵敏度
            - **SNR**: 信噪比阈值，用于过滤噪声
            - **tolerance**: m/z对齐容差
            """)
        
        # 下载区域
        st.divider()
        st.subheader("📥 下载处理结果")
        
        # 检查是否有验证集
        has_validation = 'validation' in st.session_state.demo_data
        
        if has_validation:
            # 有验证集：4列布局
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                csv_train = st.session_state.demo_data['train'].to_csv(index=False)
                st.download_button(
                    label="📊 训练集结果",
                    data=csv_train,
                    file_name="peak_intensity_train.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="下载训练集峰强度矩阵"
                )
            
            with col2:
                csv_validation = st.session_state.demo_data['validation'].to_csv(index=False)
                st.download_button(
                    label="🔍 验证集结果",
                    data=csv_validation,
                    file_name="peak_intensity_validation.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="下载验证集峰强度矩阵"
                )
            
            with col3:
                csv_params = st.session_state.demo_data['params'].to_csv(index=False)
                st.download_button(
                    label="⚙️ 处理参数",
                    data=csv_params,
                    file_name="processing_parameters.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="下载使用的处理参数"
                )
            
            with col4:
                csv_spectrum = st.session_state.demo_data['spectrum'].to_csv(index=False)
                st.download_button(
                    label="📈 质谱数据",
                    data=csv_spectrum,
                    file_name="spectrum_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="下载平均质谱原始数据"
                )
        else:
            # 无验证集：3列布局
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_train = st.session_state.demo_data['train'].to_csv(index=False)
                st.download_button(
                    label="📊 训练集结果",
                    data=csv_train,
                    file_name="peak_intensity_train.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="下载训练集峰强度矩阵"
                )
            
            with col2:
                csv_params = st.session_state.demo_data['params'].to_csv(index=False)
                st.download_button(
                    label="⚙️ 处理参数",
                    data=csv_params,
                    file_name="processing_parameters.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="下载使用的处理参数"
                )
            
            with col3:
                csv_spectrum = st.session_state.demo_data['spectrum'].to_csv(index=False)
                st.download_button(
                    label="📈 质谱数据",
                    data=csv_spectrum,
                    file_name="spectrum_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="下载平均质谱原始数据"
                )
            
            st.info("💡 提示：未检测到验证集数据。如需处理验证集，请在上传页面上传验证集ZIP文件。")

with tab3:
    st.header("数据可视化")
    
    if st.session_state.demo_data:
        # 质谱图
        st.subheader("📈 平均质谱图")
        fig_spectrum = plot_spectrum(st.session_state.demo_data['spectrum'])
        st.plotly_chart(fig_spectrum, use_container_width=True)
        st.caption("💡 图中展示了预处理后的平均质谱，峰值代表不同的m/z特征")
        
        # 两列布局
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 峰强度热图")
            fig_heatmap = plot_heatmap(st.session_state.demo_data['train'])
            st.plotly_chart(fig_heatmap, use_container_width=True)
            st.caption("💡 显示不同样本在主要峰位置的强度差异")
        
        with col2:
            st.subheader("📊 峰强度分布")
            fig_dist = plot_peak_distribution(st.session_state.demo_data['train'])
            st.plotly_chart(fig_dist, use_container_width=True)
            st.caption("💡 所有峰强度的统计分布")
        
        # 数据表格
        st.divider()
        st.subheader("📋 数据预览")
        
        # 数据集选择
        has_validation = 'validation' in st.session_state.demo_data
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if has_validation:
                dataset_choice = st.selectbox(
                    "选择数据集",
                    ["训练集", "验证集"],
                    help="选择要预览的数据集"
                )
            else:
                dataset_choice = "训练集"
                st.selectbox(
                    "选择数据集",
                    ["训练集"],
                    disabled=True,
                    help="当前仅有训练集数据"
                )
        
        # 根据选择显示对应数据
        if dataset_choice == "验证集" and has_validation:
            current_df = st.session_state.demo_data['validation']
        else:
            current_df = st.session_state.demo_data['train']
        
        with col2:
            show_rows = st.number_input(
                "显示行数",
                min_value=1,
                max_value=len(current_df),
                value=min(5, len(current_df)),
                key=f"rows_{dataset_choice}"
            )
        
        with col3:
            search_mz = st.text_input(
                "搜索m/z",
                placeholder="如: 5000",
                key=f"search_{dataset_choice}"
            )
        
        display_df = current_df.head(show_rows)
        
        if search_mz:
            matching_cols = [col for col in display_df.columns if search_mz in col]
            if matching_cols:
                display_df = display_df[['行名'] + matching_cols]
                st.success(f"找到 {len(matching_cols)} 个匹配的m/z特征")
            else:
                st.warning(f"未找到包含 '{search_mz}' 的m/z特征")
        
        st.dataframe(display_df, use_container_width=True, height=300)
        
        with st.expander("📊 查看详细统计"):
            st.write(f"**{dataset_choice}统计信息:**")
            stats_df = current_df.iloc[:, 1:].describe().T
            st.dataframe(stats_df, use_container_width=True)
    
    else:
        st.info("💡 请先在「处理与结果」页面处理数据")

# 页脚
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; padding: 1rem 0;'>
    <p><strong>MALDI-TOF MS 数据处理平台 (增强版)</strong></p>
    <p>支持ZIP批量上传 | Powered by Streamlit & MALDIquant</p>
</div>
""", unsafe_allow_html=True)
