

---

# 💬 WhatsApp Chat Analyzer 

This project provides an interactive analysis of WhatsApp chat data exported as `.txt`.
It reveals communication patterns, active hours, top users, most used words, emojis, and heatmaps of activity.

This helps users understand:

* Messaging behavior over time
* Top contributors in group chats
* Emotional tone & frequently used expressions
* Peak chat hours and active days

---

## 🚀 Tech Stack

* **Programming:** Python
* **Libraries:** Pandas, NumPy, Matplotlib, WordCloud, Emoji, Dateutil
* **Dashboard:** Streamlit
* **UI Theme:** Custom Purple Gradient UI

---

## 📂 Project Structure

```
whatsapp-chat-analyzer/
│
├─ app/
│   └─ streamlit_app.py              → Main Streamlit UI
│
├─ src/
│   ├─ __init__.py
│   ├─ parser.py                      → Converts raw chat text → structured dataframe
│   ├─ analyzer.py                    → Metrics (top words, emojis, timelines, counts)
│   ├─ visuals.py                     → WordCloud & graphical reports
│   ├─ utils.py                       → File and helper utilities
│
├─ data/
│   ├─ raw/                           → Input chat files (.txt)
│   └─ processed/                     → Cleaned & structured data
│
├─ reports/                           → Exported PNG charts
│
├─ .streamlit/
│   └─ config.toml                    → UI theme settings
│
├─ requirements.txt
└─ README.md
```

---

## 📸 Output Screenshots

### ✅ Dashboard Overview



<img width="1919" height="872" alt="image" src="https://github.com/user-attachments/assets/1c2e2b63-cf31-4f44-821c-e6f90e58ff7c" />


### 😄 Word Cloud + Emoji Usage



<img width="1916" height="880" alt="image" src="https://github.com/user-attachments/assets/778f5f9c-8578-4f47-b4e1-0a573b6cc8c2" />

## NOTE : These data are fetched real-time 
---

## 🧪 Run Locally (Windows)

### 1️⃣ Create Virtual Environment

```powershell
py -3 -m venv .venv
```

### 2️⃣ Activate Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4️⃣ Place your WhatsApp `.txt` chat file in:

```
data/raw/
```

Example:

```
data/raw/MyChat.txt
```

### 5️⃣ Run Full Processing Pipeline (Optional but Recommended)

```powershell
python -m src.cli full --input "data/raw/MyChat.txt" --workdir .
```

### 6️⃣ Run the Streamlit Dashboard

```powershell
streamlit run app/streamlit_app.py
```

Then open:

```
http://localhost:8501
```

---

## 📤 How to Export WhatsApp Chat

1. Open WhatsApp Chat
2. Tap **⋮ Menu → More → Export chat**
3. Select **Without Media**
4. Save `.txt` file
5. Upload into the dashboard

(No need to manually delete `<Media omitted>`, the system filters it automatically.)

---

## 🧠 Key Insights You Can Extract

* Who texts the most?
* Which days are most active?
* What time of day you chat most?
* Most common words (ignoring media lines)
* Most used emojis 😄🔥😢❤️

---

## 📌 Future Enhancements

* Add Sentiment Analysis (Happy / Sad / Angry message trends)
* Generate Auto PDF Report for Submission
* Multi-Chat Comparative Analytics Panel

---

## 🧑‍💻 Author

**Mithun S**
GitHub: [mithun-27](https://github.com/mithun-27)

LinkedIn: [mithun-s-732939280](https://www.linkedin.com/in/mithun-s-732939280)

---
