# Ollama LLM Application + RAG (Managed with `uv`)

โปรเจกต์ LLM ใช้งาน Local AI Model ผ่าน **Ollama** ร่วมกับระบบ **RAG (Retrieval-Augmented Generation)** สำหรับค้นหาและทำความเข้าใจเอกสารในโฟลเดอร์ [`knowledge/`](./knowledge/) โดยใช้ **`uv`** ในการจัดการ Python virtual environment และ dependencies

---

## 🚀 ฟีเจอร์

- **📚 RAG Engine (`rag_engine.py`)**:
  - อ่านไฟล์เอกสาร (`.md`, `.txt`, `.pdf`) ในโฟลเดอร์ `knowledge/`
  - สร้าง Vector Embedding ด้วยโมเดล `nomic-embed-text` ผ่าน Ollama API
  - จัดเก็บและค้นหา Vector ความสัมพันธ์ด้วย **ChromaDB**
  - ดึงเนื้อหาบริบท (Context Chunks) ที่ตรงกับคำถามมากที่สุดเพื่อแนบไปกับ Prompt
- **🌐 Web Chat UI (`app.py`)**: หน้าต่างแชท Streamlit สวยงาม
  - สวิตช์ เปิด-ปิด ระบบ RAG Knowledge Base
  - ปุ่ม Re-Index เอกสารความรู้ใหม่
  - แสดงผล **Referenced Knowledge Sources** (ชื่อไฟล์อ้างอิงและระดับความใกล้เคียง)
- **💻 CLI Chat (`cli.py`)**: โปรแกรมแชทผ่าน Terminal ด้วย `rich`
  - รองรับโหมด RAG พร้อมแสดงแหล่งอ้างอิงบน Terminal

---

## 📦 โครงสร้างโปรเจกต์

```text
.
├── knowledge/       # โฟลเดอร์เก็บเอกสารความรู้ (.md, .pdf, .txt)
├── rag_engine.py    # ระบบ RAG (Embedding, Chunking & ChromaDB Vector Store)
├── app.py           # Web UI Chat Application (Streamlit + RAG)
├── cli.py           # Terminal CLI Chat Application (Rich + RAG)
├── pyproject.toml   # การตั้งค่า dependencies ของ uv
└── README.md        # เอกสารแนะนำการใช้งาน
```

---

## ⚙️ ข้อต้องการเบื้องต้น (Prerequisites)

1. **Ollama**: ต้องลงโมเดล Chat และ Embedding ดังนี้:
   ```bash
   ollama pull qwen2.5-coder:7b
   ollama pull nomic-embed-text
   ```

---

## 💻 วิธีการรันโปรแกรมด้วย `uv`

### 1. รัน Web Chat UI (Streamlit + RAG)
```bash
uv run streamlit run app.py
```
*เปิดเว็บเบราว์เซอร์ไปที่ `http://localhost:8501`*

### 2. รัน Terminal CLI Chat (Rich + RAG)
```bash
uv run cli.py
```

---

## 🛠️ การเพิ่มเอกสารใหม่ใน RAG

1. ใส่ไฟล์เอกสาร `.md`, `.txt` หรือ `.pdf` ไว้ในโฟลเดอร์ `knowledge/`
2. กดปุ่ม **"🔄 Re-Index Knowledge Base"** บนหน้าเว็บ Streamlit หรือรัน `cli.py` ใหม่ ระบบจะสร้าง Index ใหม่อัตโนมัติ!
