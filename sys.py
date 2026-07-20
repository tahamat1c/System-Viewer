#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psutil
import platform
import socket
import time
import threading
import smtplib
from email.mime.text import MIMEText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from datetime import datetime, timedelta
import subprocess
import json

class SystemViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("System Viewer")
        self.root.geometry("1200x800")
        self.setup_theme()
        
        self.settings_file = "system_viewer_settings.json"
        self.email_config = self.load_settings()
        
        self.alert_history = []
        self.last_alert_time = None
        self.alert_cooldown = timedelta(minutes=20)
        
        # Data streams for tracking graphs
        self.cpu_data = []
        self.ram_data = []
        
        self.setup_gui()
        
        # Start safe UI refresh loop
        self.monitoring_active = True
        self.refresh_stats_loop()
        
    def load_settings(self):
        # Default placeholder template. NO hardcoded passwords here!
        default_settings = {
            'enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_from': 'your_email@gmail.com',
            'email_to': 'your_email@gmail.com',
            'username': 'your_email@gmail.com',
            'password': '',  # Enter this directly inside your local JSON file instead!
            'thresholds': {
                'cpu': 80,
                'memory': 80,
                'temp': 70
            }
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Deep merge configuration dictionary safely
                    if 'thresholds' in loaded_settings:
                        default_settings['thresholds'].update(loaded_settings['thresholds'])
                    for key in ['enabled', 'smtp_server', 'smtp_port', 'email_from', 'email_to', 'username', 'password']:
                        if key in loaded_settings:
                            default_settings[key] = loaded_settings[key]
                    return default_settings
            else:
                # Save the empty template if it doesn't exist yet
                with open(self.settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.email_config, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
        
    def setup_theme(self):
        self.root.configure(bg='#1e1e1e')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('.', background='#1e1e1e', foreground='#ffffff')
        self.style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#2d2d2d', foreground='#ffffff', padding=[10, 5], font=('Helvetica', 10, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', '#007acc')], foreground=[('selected', '#ffffff')])
        
        self.style.configure('TFrame', background='#1e1e1e')
        self.style.configure('TLabel', background='#1e1e1e', foreground='#ffffff')
        self.style.configure('TButton', background='#007acc', foreground='#ffffff', font=('Helvetica', 10), padding=5)
        self.style.map('TButton', background=[('active', '#005d9c')])
        
        self.style.configure('Treeview', background='#252526', foreground='#ffffff', fieldbackground='#252526')
        self.style.configure('Treeview.Heading', background='#2d2d2d', foreground='#ffffff')
        self.style.map('Treeview', background=[('selected', '#007acc')])
        self.style.configure('TEntry', fieldbackground='#353535', foreground='#ffffff', insertcolor='white', borderwidth=1, relief='solid')
    
    def setup_gui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_dashboard_tab()
        self.create_system_info_tab()
        self.create_process_tab()
        self.create_settings_tab()
        self.create_alert_tab()
    
    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
        
        graph_frame = ttk.Frame(self.dashboard_tab)
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # CPU Graph
        cpu_graph_frame = ttk.LabelFrame(graph_frame, text=" CPU Usage ")
        cpu_graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.cpu_fig = Figure(figsize=(5, 2), dpi=100, facecolor='#1e1e1e')
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, cpu_graph_frame)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # RAM Graph
        ram_graph_frame = ttk.LabelFrame(graph_frame, text=" RAM Usage ")
        ram_graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.ram_fig = Figure(figsize=(5, 2), dpi=100, facecolor='#1e1e1e')
        self.ram_ax = self.ram_fig.add_subplot(111)
        self.ram_canvas = FigureCanvasTkAgg(self.ram_fig, ram_graph_frame)
        self.ram_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Stats Frame
        stats_frame = ttk.LabelFrame(self.dashboard_tab, text="📈 Live Stats")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_stat_widget(stats_frame, "CPU", "#ff5555", "0%")
        self.create_stat_widget(stats_frame, "RAM", "#55aaff", "0%")
        self.create_stat_widget(stats_frame, "Temp", "#ff55ff", "0°C")
    
    def create_stat_widget(self, parent, name, color, initial_value):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        label = ttk.Label(frame, text=f"{name}:", font=('Helvetica', 12, 'bold'))
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        value = ttk.Label(frame, text=initial_value, font=('Helvetica', 12), foreground=color)
        value.pack(side=tk.LEFT)
        
        if name == "CPU": self.cpu_label = value
        elif name == "RAM": self.ram_label = value
        elif name == "Temp": self.temp_label = value
    
    def create_system_info_tab(self):
        self.info_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.info_tab, text="🖥️ System Info")
        
        info_frame = ttk.LabelFrame(self.info_tab, text=" System Information ")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.system_info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, width=80, height=20, bg='#252526', fg='#ffffff', font=('Consolas', 10))
        self.system_info_text.pack(fill=tk.BOTH, expand=True)
        self.update_system_info()
    
    def update_system_info(self):
        self.system_info_text.delete(1.0, tk.END)
        info = f"\n🌐 Hostname: {socket.gethostname()}\n🖥️ OS: {platform.system()} {platform.release()} ({platform.version()})\n🏗️ Architecture: {platform.machine()}\n⏳ Uptime: {self.format_time(psutil.boot_time())}\n"
        
        cpu_info = f"\n🔢 CPU:\n    Model: {self.get_cpu_info()}\n    Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical\n    Max Frequency: {psutil.cpu_freq().max if psutil.cpu_freq() else 0:.2f} MHz\n"
        
        ram = psutil.virtual_memory()
        ram_info = f"\n🧠 RAM:\n    Total: {ram.total / (1024**3):.2f} GB\n    Available: {ram.available / (1024**3):.2f} GB\n"
        
        self.system_info_text.insert(tk.END, info + cpu_info + ram_info)
    
    def get_cpu_info(self):
        try:
            if platform.system() == "Windows": return platform.processor()
            elif platform.system() == "Linux":
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'): return line.split(':')[1].strip()
            elif platform.system() == "Darwin":
                return subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
        except: pass
        return "Unknown"
    
    def create_process_tab(self):
        self.process_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.process_tab, text="⚙️ Processes")
        
        process_frame = ttk.LabelFrame(self.process_tab, text=" Running Processes ")
        process_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.process_tree = ttk.Treeview(process_frame, columns=("PID", "Name", "CPU%", "RAM%"), selectmode='browse')
        self.process_tree.heading("#0", text="No.", anchor=tk.W)
        self.process_tree.heading("PID", text="PID", anchor=tk.W)
        self.process_tree.heading("Name", text="Name", anchor=tk.W)
        self.process_tree.heading("CPU%", text="CPU%", anchor=tk.W)
        self.process_tree.heading("RAM%", text="RAM%", anchor=tk.W)
        
        self.process_tree.column("#0", width=50)
        self.process_tree.column("PID", width=80)
        self.process_tree.column("Name", width=200)
        self.process_tree.column("CPU%", width=80)
        self.process_tree.column("RAM%", width=80)
        
        scrollbar = ttk.Scrollbar(process_frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.process_tree.pack(fill=tk.BOTH, expand=True)
        
        refresh_btn = ttk.Button(process_frame, text="🔄 Refresh Now", command=self.update_process_list)
        refresh_btn.pack(pady=5)
    
    def create_settings_tab(self):
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        
        settings_frame = ttk.LabelFrame(self.settings_tab, text=" Alert Thresholds ")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(settings_frame, text="CPU Threshold (%):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cpu_thresh = ttk.Entry(settings_frame)
        self.cpu_thresh.insert(0, str(self.email_config['thresholds']['cpu']))
        self.cpu_thresh.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="RAM Threshold (%):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.ram_thresh = ttk.Entry(settings_frame)
        self.ram_thresh.insert(0, str(self.email_config['thresholds']['memory']))
        self.ram_thresh.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Temp Threshold (°C):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.temp_thresh = ttk.Entry(settings_frame)
        self.temp_thresh.insert(0, str(self.email_config['thresholds']['temp']))
        self.temp_thresh.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        save_btn = ttk.Button(settings_frame, text="💾 Save Settings", command=self.save_thresholds)
        save_btn.grid(row=3, columnspan=2, pady=10)
        
        # Friendly instructional alert
        instructions = (
            "💡 Tip: To run email alerts securely, check the generated file:\n"
            f"'{self.settings_file}'\n"
            "and set 'enabled': true along with your credentials there!"
        )
        ttk.Label(settings_frame, text=instructions, justify=tk.LEFT, font=('Helvetica', 9, 'italic')).grid(row=4, columnspan=2, pady=20)
    
    def create_alert_tab(self):
        self.alert_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.alert_tab, text="🔔 Alerts")
        
        alert_frame = ttk.LabelFrame(self.alert_tab, text=" Alert History ")
        alert_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.alert_text = scrolledtext.ScrolledText(alert_frame, wrap=tk.WORD, width=80, height=20, bg='#252526', fg='#ffffff', font=('Consolas', 10))
        self.alert_text.pack(fill=tk.BOTH, expand=True)
    
    def refresh_stats_loop(self):
        """Main Loop running safely on the Tkinter main thread via .after()"""
        if not self.monitoring_active:
            return
            
        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent
        
        try:
            temp = psutil.sensors_temperatures()['coretemp'][0].current
        except:
            temp = "N/A"
            
        # Update Text elements safely on main thread
        self.cpu_label.config(text=f"{cpu_percent}%")
        self.ram_label.config(text=f"{ram_percent}%")
        self.temp_label.config(text=f"{temp}°C" if temp != "N/A" else "N/A")
        
        # Check Rules
        self.check_thresholds(cpu_percent, ram_percent, temp)
        
        # Track Graph Data Arrays
        self.cpu_data.append(cpu_percent)
        self.ram_data.append(ram_percent)
        if len(self.cpu_data) > 50:
            self.cpu_data.pop(0)
            self.ram_data.pop(0)
            
        # Redraw plots
        self.update_graph(self.cpu_ax, self.cpu_canvas, self.cpu_data, "CPU Usage (%)", "#ff5555")
        self.update_graph(self.ram_ax, self.ram_canvas, self.ram_data, "RAM Usage (%)", "#55aaff")
        
        # Automatic process listing update roughly every 5 seconds
        if int(time.time()) % 5 == 0:
            self.update_process_list()
            
        # Rerun this function in 1000ms (1 second)
        self.root.after(1000, self.refresh_stats_loop)
    
    def update_graph(self, ax, canvas, data, title, color):
        ax.clear()
        ax.plot(data, color=color, linewidth=2)
        ax.set_title(title, color='white')
        ax.set_ylim(0, 100)
        ax.set_facecolor('#252526')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#007acc')
        canvas.draw()
    
    def update_process_list(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append((
                    proc.info['pid'],
                    proc.info['name'],
                    proc.info['cpu_percent'],
                    proc.info['memory_percent']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        processes.sort(key=lambda x: x[2], reverse=True)
        
        for i, (pid, name, cpu, mem) in enumerate(processes[:30], 1):  # Limit display to top 30 to prevent UI lag
            self.process_tree.insert("", tk.END, text=str(i), values=(pid, name, f"{cpu:.1f}", f"{mem:.1f}"))
    
    def check_thresholds(self, cpu, ram, temp):
        if not self.email_config.get('enabled', False):
            return
            
        current_time = datetime.now()
        if self.last_alert_time and (current_time - self.last_alert_time) < self.alert_cooldown:
            return
        
        alerts = []
        if cpu > self.email_config['thresholds']['cpu']:
            alerts.append(f"🚨 High CPU Usage: {cpu}% (Threshold: {self.email_config['thresholds']['cpu']}%)")
        if ram > self.email_config['thresholds']['memory']:
            alerts.append(f"🚨 High RAM Usage: {ram}% (Threshold: {self.email_config['thresholds']['memory']}%)")
        if temp != "N/A" and temp > self.email_config['thresholds']['temp']:
            alerts.append(f"🚨 High Temperature: {temp}°C (Threshold: {self.email_config['thresholds']['temp']}°C)")
        
        if alerts:
            alert_msg = "\n".join(alerts)
            self.log_alert(alert_msg)
            
            # Run email transmission in a background thread so the UI doesn't lock up waiting on the network connection
            threading.Thread(target=self.send_email_alert, args=(alert_msg,), daemon=True).start()
            self.last_alert_time = current_time
    
    def log_alert(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.alert_history.append(log_entry)
        self.alert_text.insert(tk.END, log_entry)
        self.alert_text.see(tk.END)
    
    def send_email_alert(self, message):
        # Double check to prevent blank password configuration failures
        if not self.email_config['password']:
            self.root.after(0, lambda: self.log_alert("❌ Missing Email Password configuration in JSON file! Skipping alert email."))
            return
            
        try:
            msg = MIMEText(message)
            msg['Subject'] = "🚨 System Alert!"
            msg['From'] = self.email_config['email_from']
            msg['To'] = self.email_config['email_to']
            
            with smtplib.SMTP(self.email_config['smtp_server'], int(self.email_config['smtp_port'])) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            # Post updates safely back to main thread log
            self.root.after(0, lambda: self.log_alert("📧 Email alert sent successfully!"))
        except Exception as e:
            self.root.after(0, lambda: self.log_alert(f"❌ Failed to send email: {str(e)}"))
    
    def save_thresholds(self):
        try:
            self.email_config['thresholds']['cpu'] = int(self.cpu_thresh.get())
            self.email_config['thresholds']['memory'] = int(self.ram_thresh.get())
            self.email_config['thresholds']['temp'] = int(self.temp_thresh.get())
            self.save_settings()
            messagebox.showinfo("Success", "Threshold settings saved configuration!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for thresholds")
    
    def format_time(self, timestamp):
        uptime_seconds = time.time() - timestamp
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{days}d {hours}h {minutes}m"
    
    def on_closing(self):
        self.monitoring_active = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemViewer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()