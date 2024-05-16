import streamlit as st
from openai import OpenAI
import os

st.title("简单翻译器",help="提示：本站未配置数据库，重新进入或刷新网页会使翻译记录消失！！！")

# 客户端
client = OpenAI(api_key = os.environ.get("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")

# 翻译记录
if "translation" not in st.session_state:
    st.session_state.translation = []

# 侧边栏
with st.sidebar:
    translation_history = st.selectbox("**翻译历史**",
                                       [history_list["content"][:10] for history_list in st.session_state.translation if history_list["role"] == "user"],
                                       index=None,help="选择翻译的历史记录。",placeholder="选择一条翻译记录")

    col1, col2 = st.columns(2)
    with col1:
        check_button = st.button("查看",key="check",help="选择好一条记录后，点击查看内容。",use_container_width=True)
    with col2:
        check_all_button = st.button("查看所有",key="all",help="查看全部历史记录。",use_container_width=True)
    
    output_button = st.button("输出成文本",key="output",help="以文本的格式查看全部历史记录，支持一键复制。",use_container_width=True)
    
    if st.button("清空记录",key="reset",help="清除全部缓存记录，慎点！",use_container_width=True):
        st.session_state.translation = []
        st.rerun()

# 页面组件
target_language = st.radio("选择你的目标语言",
                           ["English", "Chinese", "French", "Japanese", "Spanish", "Korean"],
                           horizontal=True)
origin_text = st.text_area("输入你要翻译的文本")
submit_button = st.button("提交",key="submit",type="primary",help="点击进行翻译，翻译的结果支持一键复制。")

# 消息设定
system_prompt = """你是一名翻译专家，精通多种语言。\n
你的使命是执行用户的翻译任务，请务必确保翻译结果的准确性和文本的流畅性，且符合目标语言的使用习惯。\n
请你直接给出翻译的结果，不需要附带任何说明。"""
user_message = f"请你将“{origin_text}”翻译成{target_language}"
messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}]

# 开始交互
if submit_button:
    # 记录用户的原文
    st.session_state.translation.append({"role": "user", "content": origin_text})
    # 大模型处理
    chat_completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=4096,
        temperature=1.10,
        top_p=1.00,
        frequency_penalty = 0.00,
        presence_penalty = 0.00,
        stop=None,
        stream=False
    )
    response = chat_completion.choices[0].message.content
    # 记录模型的翻译
    st.session_state.translation.append({"role": "assistant", "content": response})
    # 展示结果
    st.markdown(f"```text\n{response}\n```")

if translation_history and check_button:
    selected_index = [history_list["content"][:10] for history_list in st.session_state.translation].index(translation_history)
    callback_num = selected_index + 2
    for translation in st.session_state.translation[callback_num -2:callback_num]:
        with st.chat_message(translation["role"]):
            st.markdown(translation["content"])

if check_all_button:
    for translation in st.session_state.translation:
        with st.chat_message(translation["role"]):
            st.markdown(translation["content"])

output = ""
if output_button:
    for translation in st.session_state.translation:
        output += f"{translation["role"]}: {translation["content"]}\n"
    
    st.markdown(f"```text\n{output}\n```")