from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import openai
import os

app = FastAPI()

# 加载校园知识库
def load_knowledge():
    try:
        with open("knowledge.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "无校园知识库信息"

knowledge = load_knowledge()

# 首页网页
@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<h1>校园智能问答 RAG 系统</h1>
<div id="chat" style="height:400px;overflow:auto;border:1px solid #ddd;padding:10px"></div>
<input id="msg" style="width:80%" placeholder="提问..." />
<button onclick="send()">发送</button>
<script>
async function send(){
    let msg = document.getElementById("msg").value;
    let chat = document.getElementById("chat");
    chat.innerHTML += "<p><b>你：</b>"+msg+"</p>";
    let res = await fetch("/api/ask", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({question:msg})
    });
    let data = await res.json();
    chat.innerHTML += "<p><b>助手：</b>"+data.answer+"</p>";
    document.getElementById("msg").value="";
}
</script>
"""

# RAG 问答接口
@app.post("/api/ask")
async def ask(req: dict):
    question = req.get("question", "")
    if not question:
        return {"answer": "请输入问题"}

    # RAG 核心：把知识库 + 问题一起送给 AI
    prompt = f"""
你是校园智能助手，请根据下面的校园信息回答问题。
只根据知识库回答，不要编造。

【校园知识库】
{knowledge}

【用户问题】
{question}
"""

    try:
        client = openai.OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        resp = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role":"user","content":prompt}]
        )
        return {"answer": resp.choices[0].message.content}
    except Exception as e:
        return {"answer": f"错误：{str(e)}"}