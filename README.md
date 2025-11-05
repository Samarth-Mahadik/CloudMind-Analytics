<h1 align="center">☁️ CloudMind Analytics</h1>
<p align="center">AI-powered AWS Cost & Resource Optimization Dashboard with ML-based Wastage Prediction</p>

CloudMind Analytics intelligently scans AWS resources (EC2, EBS, S3, RDS), calculates current & potential costs, predicts future wastage trends using ML, and visualizes actionable insights on a Streamlit dashboard.

## 📅 Project Duration
**September 2025 – October 2025**

---

## 🔍 Features

✅ Fetches live AWS resource data using `boto3`  
✅ Detects underutilized AWS resources (EC2, S3, RDS, EBS)  
✅ Calculates cost & savings using AWS pricing models  
✅ Predicts future cost & wastage using AI (ML-based model)  
✅ Streamlit dashboard for cost insights & recommendations  
✅ Optional Automated alerts via AWS Lambda + EventBridge + SNS  

---

## 🧩 Project Architecture

```markdown

Data Gathering → Resource Analysis → Cost Calculation → ML Prediction → Dashboard → Alerts

````

---

## 🛠️ Tech Stack

- **Python 3.x**
- **AWS SDK (boto3)**
- **Streamlit**
- **Scikit-learn**
- **Pandas / Numpy / Matplotlib**
- **AWS (EC2, S3, RDS, Lambda, EventBridge, SNS, Cloud Watch, IAM)**

---

## 🚀 Quick Start

```markdown
```bash
git clone https://github.com/Samarth-Mahadik/CloudMind-Analytics.git
cd CloudMind-Analytics
pip install -r requirements.txt
streamlit run app/dashboard_app.py
````

---

## 🧠 ML Prediction Example

> Predicts cost trends and future wastage for idle AWS resources using regression.

<img width="1920" height="979" alt="Dashboard Screenshot" src="https://github.com/user-attachments/assets/5e49fdf3-9140-43d4-8d41-8422d0bf76d0" />


---

## 📊 Dashboard Preview

Displays:

* Resource summary
* Cost vs Savings graph
* Future wastage prediction
* Actionable recommendations

---

## 📬 Optional AWS SNS Alerts

Sends automated email when idle/underutilized resources detected.

---

## 📹 Demo Video

🎥 [Watch Demo Video](https://www.linkedin.com/posts/samarth-mahadik-8a7965339_aws-python-streamlit-activity-7386592947229724672-9Dbg?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFUJiL8Bu7meMqELvAFpli67RCHgefR5ucA)

---

## 💼 Author

**👨‍💻 Samarth Mahadik**
AWS & DevOps Enthusiast | AI + Cloud Projects | Pune, India
🔗 [LinkedIn Profile](https://www.linkedin.com/in/samarth-mahadik-8a7965339/)

---

## 🪪 License

This project is licensed under the **MIT License**.
