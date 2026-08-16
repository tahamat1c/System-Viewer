# 🖥️ System Viewer

A desktop-based **system monitoring and performance tracking application** built with Python and Tkinter. System Viewer provides real-time insights into CPU usage, RAM consumption, system temperature, running processes, and system information through a clean dark-themed graphical interface.

It also includes configurable **system threshold alerts** with optional email notifications using Gmail SMTP.

---

## 📌 Overview

System Viewer is designed to monitor the health and performance of a computer in real time.

The application continuously tracks system resources and presents the information through:

* 📊 Real-time CPU usage graphs
* 🧠 Real-time RAM usage graphs
* 🌡️ System temperature monitoring
* ⚙️ Running process monitoring
* 🖥️ Detailed system information
* 🔔 Configurable resource threshold alerts
* 📧 Optional Gmail email notifications
* ⚙️ Persistent configuration using JSON

The application uses `psutil` for system monitoring and `Tkinter` for the graphical user interface.

---

## ✨ Features

### 📊 Real-Time Dashboard

The dashboard displays live system performance information including:

* CPU usage percentage
* RAM usage percentage
* CPU usage graph
* RAM usage graph
* System temperature

The graphs maintain recent monitoring data and update automatically every second.

### 🖥️ System Information

The System Info section provides information such as:

* Hostname
* Operating system
* OS version
* System architecture
* System uptime
* CPU model
* Physical CPU cores
* Logical CPU cores
* Maximum CPU frequency
* Total RAM
* Available RAM

### ⚙️ Process Monitoring

The Processes section displays currently running processes with:

* Process ID (PID)
* Process name
* CPU usage
* RAM usage

Processes are sorted according to CPU usage, with the top 30 processes displayed to keep the interface responsive.

### 🔔 Threshold Alerts

Users can configure resource thresholds for:

* CPU usage
* RAM usage
* Temperature

When a configured threshold is exceeded, the application records an alert in the Alerts section.

A **20-minute cooldown** is implemented between alert notifications to prevent excessive alerts.

### 📧 Email Notifications

System Viewer optionally supports email notifications through Gmail SMTP.

**Important:** Gmail credentials are **not included in this repository**.

Each user must configure their own Gmail account and App Password locally.

The application stores email configuration in:

```text
system_viewer_settings.json
```

The default configuration is created automatically when the application is first executed.

### 🌙 Dark Theme

The application uses a dark-themed interface designed for comfortable monitoring and a modern desktop appearance.

---

## 🛠️ Technologies Used

* **Python 3**
* **Tkinter** — Graphical User Interface
* **psutil** — System and process monitoring
* **Matplotlib** — Real-time performance graphs
* **SMTP / smtplib** — Email notifications
* **JSON** — Local configuration storage
* **Threading** — Background email transmission

---

## 📂 Project Structure

```text
System-Viewer/
│
├── system_viewer.py
├── system_viewer_settings.json
├── README.md
└── requirements.txt
```

> `system_viewer_settings.json` contains local configuration and should not contain real credentials when committing the project to GitHub.

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/system-viewer.git
```

Move into the project directory:

```bash
cd system-viewer
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

Run the main Python file:

```bash
python system_viewer.py
```

The System Viewer desktop application will launch automatically.

---

# 📧 Gmail Email Alert Configuration

Email alerts are **optional**.

If you want to receive email notifications when CPU, RAM, or temperature exceeds the configured threshold, you need to configure your own Gmail account.

### Step 1 — Enable 2-Step Verification

Enable **2-Step Verification** on your Google account.

### Step 2 — Create a Gmail App Password

Create a **Google App Password** for the application.

Do **not** use your normal Gmail password in the application.

### Step 3 — Configure `system_viewer_settings.json`

After running the application once, the file:

```text
system_viewer_settings.json
```

will be created automatically.

Update the email configuration with your own details:

```json
{
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email_from": "your_email@gmail.com",
    "email_to": "your_email@gmail.com",
    "username": "your_email@gmail.com",
    "password": "YOUR_GMAIL_APP_PASSWORD",
    "thresholds": {
        "cpu": 80,
        "memory": 80,
        "temp": 70
    }
}
```

### ⚠️ Security Warning

**Never upload your real Gmail password or App Password to GitHub.**

For a public repository, keep the configuration as a template and add the actual credentials only to your local copy.

You can also add the configuration file to `.gitignore`:

```gitignore
system_viewer_settings.json
venv/
__pycache__/
*.pyc
```

---

## ⚙️ Configurable Thresholds

The default thresholds are:

| Resource    | Default Threshold |
| ----------- | ----------------: |
| CPU         |               80% |
| RAM         |               80% |
| Temperature |              70°C |

These values can be changed directly from the **Settings** tab.

Click:

```text
Settings → Save Settings
```

to save the new thresholds.

---

## 🔔 Alert System

When monitoring detects a value above its configured threshold, System Viewer creates an alert.

Example:

```text
🚨 High CPU Usage: 92% (Threshold: 80%)
```

Alerts are displayed in the **Alerts** tab.

If email notifications are enabled and configured correctly, the alert is also sent through Gmail SMTP.

---

## 🧠 How It Works

```text
              ┌─────────────────────┐
              │    System Viewer    │
              └──────────┬──────────┘
                         │
             ┌───────────▼───────────┐
             │       psutil          │
             │ System Monitoring     │
             └───────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
      CPU              RAM           Temperature
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                Threshold Checking
                         │
                  ┌──────┴──────┐
                  │             │
                 Safe          Alert
                  │             │
                  ▼             ▼
              Continue      Alert Log
                                │
                                ▼
                         Optional Email
```

---

## 📈 Performance Monitoring

The application refreshes system statistics approximately every second.

CPU and RAM usage are continuously collected and displayed through Matplotlib graphs.

The graph history is limited to the most recent **50 data points** to prevent unnecessary memory usage.

Process information is also refreshed periodically, displaying the top 30 processes by CPU usage.

---

## 🔐 Security

System Viewer does not include hardcoded email passwords.

Email credentials are loaded from the local JSON configuration file.

For public GitHub repositories:

* Never commit real passwords
* Never commit Gmail App Passwords
* Keep `system_viewer_settings.json` out of version control if it contains credentials
* Use a configuration template for other users

---

## 🖥️ Supported Platforms

The application is designed to work with operating systems supported by Python and the required libraries.

CPU information handling includes support for:

* Windows
* Linux
* macOS

Some hardware temperature sensors may not be available on every system. When temperature information cannot be obtained, the application displays:

```text
N/A
```

---

## 📦 Requirements

Main dependencies:

```text
psutil
matplotlib
```

Tkinter is also required for the graphical interface.

On many Python installations, Tkinter is included with Python. Some Linux distributions may require installing it separately through the operating system package manager.

---

## 🎯 Project Purpose

This project was developed to demonstrate practical implementation of:

* Desktop GUI development
* System resource monitoring
* Real-time data visualization
* Process management
* Threshold-based alert systems
* SMTP email integration
* JSON-based configuration
* Background task execution
* Cross-platform system information retrieval

---

## 🔮 Future Improvements

Possible future improvements include:

* 📊 Disk usage monitoring
* 🌐 Network usage monitoring
* 💾 Disk health monitoring
* 🔋 Battery monitoring
* 📈 More advanced performance analytics
* 📁 Persistent alert history
* 🔔 Desktop notifications
* 📧 Multiple email recipients
* 📱 Remote monitoring dashboard
* 🔐 Encrypted credential storage
* 📊 Historical performance reports

---

## 👨‍💻 Author

**Syed Taha Manzar**

---

## 📄 License

This project is available for educational and personal use.
