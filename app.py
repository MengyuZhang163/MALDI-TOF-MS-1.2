import streamlit as st
import pandas as pd
import subprocess
import tempfile
import shutil
from pathlib import Path
import zipfile
import io

# 页面配置
st.set_page_config(
    page_title="MALDI-TOF MS 模版化处理平台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .phase-header {
        background: linear-gradient(90deg, #1f77b4 0%, #4a9eff 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 1.3rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'template_created' not in st.session_state:
    st.session_state.template_created = False
if 'template_data' not in st.session_state:
    st.session_state.template_data = None

def extract_files_from_zip(zip_file):
    """从ZIP文件中提取TXT和Excel文件"""
    txt_files = []
    excel_file = None
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.lower().endswith('.txt') and not file_name.startswith('__MACOSX'):
                txt_files.append((file_name, zip_ref.read(file_name)))
            elif file_name.lower().endswith(('.xlsx', '.xls')) and not file_name.startswith('__MACOSX'):
                if excel_file is None:
                    excel_file = (file_name, zip_ref.read(file_name))
    
    return txt_files, excel_file

def check_r_installation():
    """检查R是否安装"""
    try:
        result = subprocess.run(['Rscript', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except:
        return False

def run_r_script(script_content, work_dir):
    """执行R脚本"""
    script_path = Path(work_dir) / "process.R"
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    try:
        result = subprocess.run(
            ['Rscript', str(script_path)],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=600
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "处理超时（超过10分钟）", 1
    except Exception as e:
        return "", f"执行R脚本出错: {str(e)}", 1

# 主界面
st.markdown('<div class="main-header">🔬 MALDI-TOF MS 模版化处理平台</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">基于训练集建立特征模版，批量处理验证集</div>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("📋 处理策略")
    st.info("""
    **模版化处理流程：**
    
    1️⃣ **阶段1**：处理训练集
       - 上传训练集ZIP
       - 建立特征模版
       - 保存参数配置
    
    2️⃣ **阶段2**：处理验证集
       - 使用训练集模版
       - 批量处理多批次
       - 特征完全一致
    """)
    
    st.divider()
    
    st.header("⚙️ 处理参数")
    
    with st.expander("高级参数设置", expanded=False):
        halfWindowSize = st.slider("半峰宽", 10, 200, 90, 10)
        SNR = st.slider("信噪比阈值", 1.0, 10.0, 2.0, 0.5)
        tolerance = st.slider("对齐容差", 0.001, 0.02, 0.008, 0.001, format="%.4f")
        iterations = st.slider("基线去除迭代次数", 50, 200, 100, 10)
    
    processing_params = {
        'halfWindowSize': halfWindowSize,
        'SNR': SNR,
        'tolerance': tolerance,
        'iterations': iterations
    }
    
    st.divider()
    
    # 检查R环境
    st.header("🔧 环境检查")
    if check_r_installation():
        st.success("✅ R环境已安装")
    else:
        st.error("❌ 未检测到R环境")

# 主内容区
tab1, tab2 = st.tabs(["🎯 阶段1: 建立训练集模版", "🔄 阶段2: 处理验证集"])

# 阶段1: 建立训练集模版
with tab1:
    st.markdown('<div class="phase-header">📊 阶段1: 建立训练集特征模版</div>', unsafe_allow_html=True)
    
    st.info("💡 处理训练集并建立特征模版（只需做一次！）")
    
    train_zip = st.file_uploader("上传训练集ZIP文件", type=['zip'], key='train_zip')
    
    if train_zip:
        txt_files, excel_file = extract_files_from_zip(train_zip)
        
        if txt_files and excel_file:
            st.success(f"✅ {len(txt_files)}个TXT文件 + 1个Excel文件")
            
            if st.button("🎯 建立训练集模版", type="primary", use_container_width=True):
                # 处理逻辑（简化版，完整代码太长）
                st.info("正在处理...")

# 阶段2: 处理验证集
with tab2:
    st.markdown('<div class="phase-header">🔄 阶段2: 使用模版处理验证集</div>', unsafe_allow_html=True)
    
    if not st.session_state.template_created:
        st.warning("⚠️ 请先完成阶段1！")
    else:
        st.success("✅ 特征模版已就绪！")
        
        valid_zip = st.file_uploader("上传验证集ZIP文件", type=['zip'], key='valid_zip')
        
        if valid_zip:
            if st.button("🔄 处理验证集", type="primary", use_container_width=True):
                st.info("正在处理...")

st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p><strong>MALDI-TOF MS 模版化处理平台</strong></p>
</div>
""", unsafe_allow_html=True)
