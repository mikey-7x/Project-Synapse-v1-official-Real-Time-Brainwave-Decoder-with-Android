# ==============================================================================
# PROJECT SYNAPSE powered by [mikey:hexoid-sys]
# Copyright (c) 2026 mikey-7x
# Edition: Precision Augmentation & Advanced Extraction Core
# ==============================================================================
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import socket, threading, time, struct, json, os, shutil, warnings
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.signal import butter, filtfilt, iirnotch, welch, find_peaks
from scipy.stats import entropy, skew, kurtosis
import joblib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Bidirectional, Conv1D, MaxPooling1D, BatchNormalization
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences

warnings.filterwarnings('ignore')

# ==============================================================================
# [mikey:hexoid-sys] NATIVE TRINX-FIRST AI PACKAGE
# ==============================================================================
class TrinxEngine:
    def __init__(self):
        self.memory_bank = []
        self.labels = []

    def fit(self, X_variable_lengths, y_labels):
        self.memory_bank = X_variable_lengths
        self.labels = y_labels
        print(f"[mikey:hexoid-sys] TRINX-FIRST ENGINE LOADED {len(X_variable_lengths)} DYNAMIC TRINXS.")

    def _fast_dtw(self, trinx_a, trinx_b):
        n, m = len(trinx_a), len(trinx_b)
        dtw_matrix = np.full((n + 1, m + 1), np.inf)
        dtw_matrix[0, 0] = 0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = abs(trinx_a[i - 1] - trinx_b[j - 1])
                dtw_matrix[i, j] = cost + min(dtw_matrix[i - 1, j],    
                                              dtw_matrix[i, j - 1],    
                                              dtw_matrix[i - 1, j - 1]) 
        return dtw_matrix[n, m]

    def predict(self, live_trinx):
        if not self.memory_bank: return -1, 0.0

        live_std = np.std(live_trinx) + 1e-8
        live_norm = (live_trinx - np.mean(live_trinx)) / live_std
        
        distances = []
        for i, stored_trinx in enumerate(self.memory_bank):
            stored_std = np.std(stored_trinx) + 1e-8
            stored_norm = (stored_trinx - np.mean(stored_trinx)) / stored_std
            
            dist = self._fast_dtw(live_norm, stored_norm)
            norm_dist = dist / (len(live_norm) + len(stored_norm))
            distances.append((norm_dist, self.labels[i]))

        distances.sort(key=lambda x: x[0])
        top_match = distances[0]
        best_label = top_match[1]
        
        raw_conf = np.clip(100.0 - (top_match[0] * 70.0), 0.0, 100.0)
        
        top_3 = [d[1] for d in distances[:3]]
        if top_3.count(best_label) >= 2:
            raw_conf = min(100.0, raw_conf + 10.0)

        return best_label, raw_conf

# ==============================================================================
# INFRASTRUCTURE & GUI
# ==============================================================================
def establish_storage():
    android_path = "/storage/emulated/0/Documents/Project_Synapse"
    local_path = "Synapse_Memory"
    try:
        os.makedirs(android_path, exist_ok=True)
        return android_path
    except: return local_path

BASE_DIR = establish_storage()
DATA_DIR = os.path.join(BASE_DIR, "EEG_Data")
MODELS_DIR = os.path.join(BASE_DIR, "Models")
LABELS_FILE = os.path.join(MODELS_DIR, "labels.json")
LSTM_MODEL_FILE = os.path.join(MODELS_DIR, "brain_model_lstm.keras")
GRU_MODEL_FILE = os.path.join(MODELS_DIR, "brain_model_gru.keras")

class QuantumSynapseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PROJECT SYNAPSE By Mikey-7x")
        self.root.geometry("500x980")
        self.root.configure(bg="#050505")

        self.tcp_socket = None
        self.is_connected = False
        self.sample_rate = 140 
        
        self.buffer_size = self.sample_rate * 4 
        self.data_buffer = np.zeros(self.buffer_size)
        
        self.recording_buffer = []
        self.all_strips = []
        
        self.last_a0 = 0
        self.last_a1 = 0
        self.last_ac = 0
        
        self.trinx_ai = TrinxEngine()
        
        self.models = {
            "trinx-first (Native Dynamic AI)": self.trinx_ai,
            "CNN-LSTM (Deep Learning)": None,
            "CNN-GRU (Deep Learning)": None,
            "XGBoost": XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05), 
            "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=15),
            "SVM": SVC(probability=True, kernel='rbf', C=10),
            "KNN": KNeighborsClassifier(n_neighbors=3, weights='distance'),
            "Log Regression": LogisticRegression(max_iter=2000)
        }

        self.model_status = {k: False for k in self.models.keys()}
        self.active_model_name = "trinx-first (Native Dynamic AI)"
        self.labels_map = []
        self.is_trained = False
        self.max_trinx_len = 280
        
        self.is_recording = False
        self.is_predicting = False
        self.is_training = False 
        self.is_speaking = False 
        self.target_word = ""
        self.strips_collected = 0
        self.strip_start_time = 0
        self.last_pred_time = 0
        
        self.auto_heal_filesystem()
        self.build_ui()

    def auto_heal_filesystem(self):
        for d in [DATA_DIR, MODELS_DIR]: os.makedirs(d, exist_ok=True)
        self.is_trained = False
        for k in self.model_status: self.model_status[k] = False

        current_classes = sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])
        
        valid_classes = []
        for c in current_classes:
            folder = os.path.join(DATA_DIR, c)
            if len(os.listdir(folder)) == 0:
                shutil.rmtree(folder)
            else:
                valid_classes.append(c)
        current_classes = valid_classes

        saved_labels = []
        if os.path.exists(LABELS_FILE):
            try:
                with open(LABELS_FILE, 'r') as f:
                    saved_labels = json.load(f)
            except: pass

        if saved_labels != current_classes and len(saved_labels) > 0:
            print("[mikey:hexoid-sys] FOLDER TAMPERING DETECTED! Purging stale models to prevent Ghost Predictions.")
            for f in os.listdir(MODELS_DIR):
                try: os.remove(os.path.join(MODELS_DIR, f))
                except: pass
            self.labels_map = current_classes
            return 

        self.labels_map = current_classes

        if len(self.labels_map) > 0:
            for name in list(self.models.keys()):
                if "Deep Learning" in name or "trinx" in name: continue
                path = os.path.join(MODELS_DIR, f"{name.replace(' ', '_')}.joblib")
                if os.path.exists(path):
                    try:
                        self.models[name] = joblib.load(path)
                        self.model_status[name] = True
                        self.is_trained = True
                    except: os.remove(path)
                    
            if os.path.exists(LSTM_MODEL_FILE):
                try:
                    self.models["CNN-LSTM (Deep Learning)"] = load_model(LSTM_MODEL_FILE)
                    self.model_status["CNN-LSTM (Deep Learning)"] = True
                except: pass
                
            if os.path.exists(GRU_MODEL_FILE):
                try:
                    self.models["CNN-GRU (Deep Learning)"] = load_model(GRU_MODEL_FILE)
                    self.model_status["CNN-GRU (Deep Learning)"] = True
                except: pass
                
            if self.model_status["CNN-LSTM (Deep Learning)"] or self.model_status["XGBoost"]:
                self.rebuild_trinx_memory()

    def rebuild_trinx_memory(self):
        try:
            X_trinx_raw, y_trinx = [], []
            max_len = 0
            for idx, label in enumerate(self.labels_map):
                sub = os.path.join(DATA_DIR, label)
                for fname in os.listdir(sub):
                    sig = pd.read_csv(os.path.join(sub, fname))['signal'].values
                    X_trinx_raw.append(sig)
                    y_trinx.append(idx)
                    if len(sig) > max_len: max_len = len(sig)
            
            if len(X_trinx_raw) > 0:
                self.trinx_ai.fit(X_trinx_raw, y_trinx)
                self.models["trinx-first (Native Dynamic AI)"] = self.trinx_ai
                self.model_status["trinx-first (Native Dynamic AI)"] = True
                self.max_trinx_len = max(max_len, 280)
        except: pass

    def reset_system(self):
        if self.is_training: return messagebox.showwarning("Warning", "Network is compiling.")
        if messagebox.askyesno("DANGER", "Delete all trained data and models?"):
            self.is_predicting = False
            self.btn_predict.config(text="▶ START PREDICTING", bg="#444")
            if os.path.exists(DATA_DIR): shutil.rmtree(DATA_DIR)
            if os.path.exists(MODELS_DIR): shutil.rmtree(MODELS_DIR)
            os.makedirs(DATA_DIR, exist_ok=True)
            os.makedirs(MODELS_DIR, exist_ok=True)
            self.labels_map = []
            self.is_trained = False
            for k in self.model_status: self.model_status[k] = False
            self.models["CNN-LSTM (Deep Learning)"] = None
            self.models["CNN-GRU (Deep Learning)"] = None
            self.trinx_ai = TrinxEngine()
            self.models["trinx-first (Native Dynamic AI)"] = self.trinx_ai
            self.lbl_ai_out.config(text="[ SYSTEM MEMORY WIPED ]", fg="#ff4444")

    def build_ui(self):
        tk.Label(self.root, text="PROJECT SYNAPSE v19.0", font=("Consolas", 20, "bold"), fg="#00ffff", bg="#050505").pack(pady=(5,0))
        tk.Label(self.root, text="powered by [mikey:hexoid-sys]", font=("Consolas", 10, "bold"), fg="#00ff00", bg="#050505").pack()
        
        conn_frame = tk.Frame(self.root, bg="#111", bd=1, relief="ridge")
        conn_frame.pack(pady=5, padx=10, fill="x")
        
        tk.Label(conn_frame, text="Port:", bg="#111", fg="#fff", font=("Arial", 10)).pack(side="left", padx=(10, 2))
        self.port_var = tk.StringVar(value="5656")
        tk.Entry(conn_frame, textvariable=self.port_var, width=6, bg="#222", fg="#00ffff", font=("Consolas", 10, "bold"), insertbackground="white").pack(side="left")
        
        self.btn_connect = tk.Button(conn_frame, text="CONNECT", bg="#006600", fg="white", font=("Arial", 9, "bold"), command=self.toggle_connection)
        self.btn_connect.pack(side="left", padx=10, pady=5)
        self.lbl_status = tk.Label(conn_frame, text="◉ OFFLINE", fg="#ff3333", bg="#111", font=("Consolas", 10, "bold"))
        self.lbl_status.pack(side="right", padx=10)

        self.fig, (self.ax_wave, self.ax_freq) = plt.subplots(2, 1, figsize=(4.5, 4.0), facecolor='#050505')
        self.fig.tight_layout(pad=2.0)
        
        self.ax_wave.set_facecolor('#000000')
        self.line_wave, = self.ax_wave.plot(np.zeros(280), color="#00ffff", lw=1.2)
        self.ax_wave.set_ylim(-2, 2) 
        self.ax_wave.axis('off')
        
        self.ax_freq.set_facecolor('#000000')
        self.freq_bars = self.ax_freq.bar(['δ', 'θ', 'α', 'β', 'γ'], [0,0,0,0,0], color=['#ff4444', '#ffaa00', '#44ff44', '#00ffff', '#cc44ff'])
        self.ax_freq.set_ylim(0, 10)
        self.ax_freq.tick_params(colors='#555555')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(pady=5)
        self.ani = animation.FuncAnimation(self.fig, self.update_dashboard, interval=50, blit=False)

        telemetry_frame = tk.Frame(self.root, bg="#050505")
        telemetry_frame.pack(pady=5, fill="x")
        
        self.lbl_raw_adc = tk.Label(telemetry_frame, text="ADC: A0 [0] | A1 [0] | AC [0]", font=("Consolas", 11, "bold"), fg="#ff00ff", bg="#050505")
        self.lbl_raw_adc.pack()
        
        self.lbl_state = tk.Label(telemetry_frame, text="STATE: WAITING...", font=("Consolas", 12, "bold"), fg="#aaaaaa", bg="#050505")
        self.lbl_state.pack()
        self.lbl_exact_freq = tk.Label(telemetry_frame, text="FREQ: 0.0 Hz", font=("Consolas", 11), fg="#ffaa00", bg="#050505")
        self.lbl_exact_freq.pack()

        ai_frame = tk.Frame(self.root, bg="#111", bd=1, relief="ridge")
        ai_frame.pack(pady=5, padx=10, fill="x")
        
        ctrl_top = tk.Frame(ai_frame, bg="#111")
        ctrl_top.pack(fill="x", pady=5)
        self.btn_train = tk.Button(ctrl_top, text="[TRAIN TRINX]", bg="#0055aa", fg="white", font=("Arial", 9, "bold"), command=self.start_training)
        self.btn_train.pack(side="left", padx=10)
        
        self.model_var = tk.StringVar(value=self.active_model_name)
        combo = ttk.Combobox(ctrl_top, textvariable=self.model_var, values=list(self.models.keys()), width=23, state="readonly")
        combo.pack(side="right", padx=10)
        combo.bind("<<ComboboxSelected>>", self.change_model)

        ctrl_bottom = tk.Frame(ai_frame, bg="#111")
        ctrl_bottom.pack(fill="x", pady=5)
        self.btn_predict = tk.Button(ctrl_bottom, text="▶ START PREDICTING", bg="#444", fg="white", font=("Arial", 10, "bold"), command=self.toggle_prediction)
        self.btn_predict.pack(side="left", fill="x", expand=True, padx=(10, 5))
        self.btn_reset = tk.Button(ctrl_bottom, text="[X] RESET", bg="#aa0000", fg="white", font=("Arial", 10, "bold"), command=self.reset_system)
        self.btn_reset.pack(side="right", padx=(5, 10))

        self.lbl_ai_out = tk.Label(self.root, text="[ SYSTEM OPTIMAL ]" if self.is_trained else "[ AWAITING TRAINING ]", font=("Consolas", 14, "bold"), fg="#00ff00" if self.is_trained else "#ffff00", bg="#050505")
        self.lbl_ai_out.pack(pady=10)
        
        tk.Label(self.root, text="Copyright (c) 2026 mikey-7x", font=("Consolas", 8), fg="#555555", bg="#050505").pack(side="bottom", pady=5)

    def change_model(self, event): 
        self.active_model_name = self.model_var.get()
        if self.model_status.get(self.active_model_name, False):
            self.lbl_ai_out.config(text=f"[ {self.active_model_name} READY ]", fg="#00ff00")
        else:
            self.lbl_ai_out.config(text=f"[ {self.active_model_name} UNTRAINED ]", fg="#ff4444")

    def toggle_connection(self):
        if not self.is_connected:
            try:
                port = int(self.port_var.get())
                threading.Thread(target=self.tcp_reader_thread, args=(port,), daemon=True).start()
            except: messagebox.showerror("Error", "Invalid Port Number.")
        else:
            self.is_connected = False
            if self.tcp_socket:
                try: self.tcp_socket.close()
                except: pass

    def tcp_reader_thread(self, port):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.settimeout(2.0)
        try:
            self.tcp_socket.connect(('127.0.0.1', port))
            self.is_connected = True
            self.root.after(0, lambda: self.btn_connect.config(text="DISCONNECT", bg="#aa0000"))
            self.root.after(0, lambda: self.lbl_status.config(text="◉ LIVE", fg="#00ffff"))
            
            raw_buffer = bytearray()
            
            while self.is_connected:
                try:
                    chunk = self.tcp_socket.recv(8192) 
                    if not chunk: continue
                    raw_buffer.extend(chunk)
                    
                    new_values = []
                    
                    while len(raw_buffer) >= 6:
                        sync_idx = raw_buffer.find(b'\xAA\x55')
                        
                        if sync_idx == -1:
                            if len(raw_buffer) > 0 and raw_buffer[-1] == 0xAA:
                                del raw_buffer[:-1]
                            else:
                                raw_buffer.clear()
                            break
                            
                        if sync_idx > 0:
                            del raw_buffer[:sync_idx]
                            
                        if len(raw_buffer) < 6:
                            break
                            
                        a0, a1 = struct.unpack('>hh', raw_buffer[2:6])
                        true_ac = a0 - a1
                        self.last_a0, self.last_a1, self.last_ac = a0, a1, true_ac
                        new_values.append(true_ac)
                        del raw_buffer[:6]
                        
                    if new_values:
                        n_new = len(new_values)
                        if n_new >= self.buffer_size:
                            self.data_buffer[:] = new_values[-self.buffer_size:]
                        else:
                            self.data_buffer = np.roll(self.data_buffer, -n_new)
                            self.data_buffer[-n_new:] = new_values
                            
                        if self.is_recording:
                            self.recording_buffer.extend(new_values)

                except socket.timeout: continue 
                except: pass 
        except: pass
        finally:
            self.is_connected = False
            self.root.after(0, lambda: self.btn_connect.config(text="CONNECT", bg="#006600"))
            self.root.after(0, lambda: self.lbl_status.config(text="◉ OFFLINE", fg="#ff3333"))

    def preprocess_signal(self, sig):
        sig = sig - np.mean(sig)
        try:
            b, a = iirnotch(50.0, 30.0, self.sample_rate)
            sig = filtfilt(b, a, sig)
            b, a = butter(2, [1.0/(0.5*self.sample_rate), 40.0/(0.5*self.sample_rate)], btype='band')
            sig = filtfilt(b, a, sig)
        except: pass
        return np.nan_to_num(sig, nan=0.0, posinf=0.0, neginf=0.0)

    def extract_features(self, buffer):
        freqs, psd = welch(buffer, fs=self.sample_rate, nperseg=min(len(buffer), 140))
        def bp(lo, hi):
            idx = (freqs >= lo) & (freqs < hi)
            return np.mean(psd[idx]) if np.any(idx) else 0.0

        bands = [bp(0.5, 4), bp(4, 8), bp(8, 13), bp(13, 30), bp(30, 45)]
        peak_freq = freqs[np.argmax(psd)] if len(freqs) > 0 else 0.0

        mav = np.mean(np.abs(buffer))
        rms = np.sqrt(np.mean(buffer**2))
        
        if len(buffer) > 2:
            zcr = np.sum(np.diff(np.sign(buffer)) != 0)
            line_len = np.sum(np.abs(np.diff(buffer)))
            ssc = np.sum(np.diff(np.sign(np.diff(buffer))) != 0) 
            dx, ddx = np.diff(buffer), np.diff(np.diff(buffer))
            var_x, var_dx, var_ddx = np.var(buffer), np.var(dx), np.var(ddx)
        else:
            zcr, line_len, ssc, var_dx, var_ddx = 0, 0, 0, 0, 0
            var_x = np.var(buffer)

        mobility = np.sqrt(var_dx / var_x) if var_x > 0 else 0
        complexity = (np.sqrt(var_ddx / var_dx) / mobility) if (var_dx > 0 and mobility > 0) else 0

        features = bands + [
            mav, rms, zcr, line_len, ssc,
            np.mean(buffer), np.std(buffer), var_x, np.ptp(buffer),
            skew(buffer), kurtosis(buffer),
            mobility, complexity, entropy(psd + 1e-12)
        ]
        
        return np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0).tolist(), peak_freq, bands

    def update_dashboard(self, frame):
        try:
            if not self.is_connected: return

            self.lbl_raw_adc.config(text=f"ADC: A0 [{self.last_a0}] | A1 [{self.last_a1}] | AC [{self.last_ac}]")
            
            clean_full_buffer = self.preprocess_signal(self.data_buffer.copy())
            clean_view = clean_full_buffer[-280:] 
            features, peak_freq, bands = self.extract_features(clean_view)
            
            self.line_wave.set_ydata(clean_view)
            
            dynamic_limit = np.percentile(np.abs(clean_view), 99) * 1.5
            if dynamic_limit < 500.0: dynamic_limit = 500.0 
            self.ax_wave.set_ylim(-dynamic_limit, dynamic_limit)
            
            max_amp = np.max(np.abs(clean_view))

            if max_amp < 100.0: 
                self.lbl_state.config(text="STATE: [-] NO SIGNAL", fg="#555555")
                self.lbl_exact_freq.config(text="FREQ: 0.0 Hz")
                for bar in self.freq_bars: bar.set_height(0)
                self.ax_freq.set_ylim(0, 5)
            else:
                self.lbl_exact_freq.config(text=f"FREQ: {peak_freq:.1f} Hz")
                for bar, h in zip(self.freq_bars, bands): bar.set_height(h)
                self.ax_freq.set_ylim(0, max(max(bands), 2) * 1.2)
                
                if peak_freq < 4.0: self.lbl_state.config(text="STATE: [~] DELTA", fg="#ff4444")
                elif 4.0 <= peak_freq < 8.0: self.lbl_state.config(text="STATE: [@] THETA", fg="#ffaa00")
                elif 8.0 <= peak_freq < 13.0: self.lbl_state.config(text="STATE: [+] ALPHA", fg="#44ff44")
                elif 13.0 <= peak_freq < 30.0: self.lbl_state.config(text="STATE: [*] BETA", fg="#00ffff")
                else: self.lbl_state.config(text="STATE: [#] GAMMA", fg="#cc44ff")

            if self.is_recording:
                elapsed = time.time() - self.strip_start_time
                if elapsed >= 10.0: 
                    strip_data = list(self.recording_buffer)
                    self.recording_buffer.clear()
                    self.all_strips.append(strip_data)
                    self.strips_collected += 1
                    self.strip_start_time = time.time() 
                    
                    if self.strips_collected >= 6:
                        self.is_recording = False
                        self.is_training = True 
                        self.lbl_ai_out.config(text="[ ALL STRIPS CAPTURED. EXTRACTING TRINXS... ]", fg="#00ff00")
                        self.root.after(500, lambda: threading.Thread(target=self.extract_trinxs_and_train, daemon=True).start()) 
                    else:
                        self.lbl_ai_out.config(text=f"[ RECORDING STRIP {self.strips_collected + 1}/6 : KEEP THINKING... ]", fg="#ff00ff")
                        
            elif self.is_predicting and not self.is_training:
                current_time = time.time()
                
                if max_amp > 500.0:
                    self.is_speaking = True
                    self.lbl_ai_out.config(text="[ CAPTURING TRINX SHAPE... ]", fg="#ffff00")
                    
                elif self.is_speaking and max_amp < 200.0:
                    self.predict_live_signal(clean_full_buffer.copy())
                    self.is_speaking = False
                    self.last_pred_time = current_time 
                    
                elif not self.is_speaking:
                    if current_time - self.last_pred_time >= 1.0:
                        self.lbl_ai_out.config(text="[ AWAITING TRINX BURST... ]", fg="#aaaaaa")

        except Exception as e: pass 

    def start_training(self):
        if self.is_training: return
        if not self.is_connected: return messagebox.showerror("Error", "Connect Bridge First!")
        if self.is_predicting: self.toggle_prediction()
        word = simpledialog.askstring("Train Word", "Enter word to repeatedly focus on:")
        if word:
            self.target_word = word.lower().strip()
            self.strips_collected = 0
            self.all_strips = []
            self.recording_buffer.clear()
            self.is_recording = True
            self.strip_start_time = time.time()
            self.lbl_ai_out.config(text=f"[ RECORDING STRIP 1/6 : KEEP THINKING... ]", fg="#ff00ff")

    # =========================================================================
    # [mikey:hexoid-sys] AUTOCORRELATION SLICER 
    # =========================================================================
    def extract_trinxs_and_train(self):
        try:
            target_dir = os.path.join(DATA_DIR, self.target_word)
            os.makedirs(target_dir, exist_ok=True)
            
            full_signal = []
            for strip in self.all_strips: full_signal.extend(strip)
            sig = np.array(full_signal)
            clean = self.preprocess_signal(sig)
            
            envelope = pd.Series(np.abs(clean)).rolling(window=70, center=True).mean().fillna(0).values
            autocorr = np.correlate(envelope, envelope, mode='full')[len(envelope)-1:]
            
            peaks, _ = find_peaks(autocorr, distance=70) 
            
            if len(peaks) > 0:
                period_T = peaks[0] 
            else:
                period_T = 140 * 2 
                
            period_T = max(70, min(period_T, 140 * 3))
            
            num_slices = len(clean) // period_T
            extracted_count = 0
            
            for i in range(num_slices):
                start = i * period_T
                end = start + period_T
                exact_trinx = clean[start:end]
                
                if np.max(np.abs(exact_trinx)) > 200.0:
                    fname = f"{self.target_word}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{extracted_count}.csv"
                    pd.DataFrame({"signal": exact_trinx}).to_csv(os.path.join(target_dir, fname), index=False)
                    extracted_count += 1

            if extracted_count < 5:
                raise ValueError("Signal too weak to extract valid Trinxs.")

            print(f"[mikey:hexoid-sys] Engine Extracted {extracted_count} Dynamic Trinxs of {period_T} length.")
            self.train_models_backend()
            
        except Exception as e:
            print(f"Trinx Error: {e}")
            shutil.rmtree(os.path.join(DATA_DIR, self.target_word))
            self.is_training = False
            self.root.after(0, lambda: self.lbl_ai_out.config(text=f"[ EXTRACTION FAILED: SIGNAL TOO LOW ]", fg="#ff0000"))

    def train_models_backend(self):
        self.root.after(0, lambda: self.lbl_ai_out.config(text="[ COMPILING AI CORES WITH DATA AUGMENTATION... ]", fg="#ffff00"))
        self.auto_heal_filesystem()
        
        X_trinx_raw = []
        y_trinx = []
        X_feat = []
        
        if len(self.labels_map) < 2:
            self.is_training = False
            self.root.after(0, lambda: self.lbl_ai_out.config(text=f"[ ERROR: TRAIN AT LEAST 2 DIFFERENT WORDS ]", fg="#ff4444"))
            return

        max_len_found = 0
        for idx, label in enumerate(self.labels_map):
            sub = os.path.join(DATA_DIR, label)
            for fname in os.listdir(sub):
                try:
                    sig = pd.read_csv(os.path.join(sub, fname))['signal'].values
                    X_trinx_raw.append(sig)
                    y_trinx.append(idx)
                    if len(sig) > max_len_found: max_len_found = len(sig)
                    
                    feats, _, _ = self.extract_features(sig)
                    X_feat.append(feats)
                    
                    # --- DATA AUGMENTATION (Injects 3 Synthetic variations per Trinx) ---
                    for _ in range(3):
                        noise = np.random.normal(0, 0.05 * np.std(sig), sig.shape)
                        aug_sig = sig + noise
                        X_trinx_raw.append(aug_sig)
                        y_trinx.append(idx)
                        
                        aug_feats, _, _ = self.extract_features(aug_sig)
                        X_feat.append(aug_feats)
                        
                except: pass

        if len(X_trinx_raw) < 10:
            self.is_training = False
            self.root.after(0, lambda: self.lbl_ai_out.config(text=f"[ ERROR: INSUFFICIENT TRINX DATA ]", fg="#ff4444"))
            return

        # 1. Native Trinx AI 
        self.trinx_ai = TrinxEngine()
        self.trinx_ai.fit(X_trinx_raw, y_trinx)
        self.models["trinx-first (Native Dynamic AI)"] = self.trinx_ai
        self.model_status["trinx-first (Native Dynamic AI)"] = True 
        
        self.max_trinx_len = max(max_len_found, 280)

        # 2. Classical Machine Learning
        self.root.after(0, lambda: self.lbl_ai_out.config(text="[ TRAINING CLASSICAL ML... ]", fg="#ffff00"))
        X_feat = np.nan_to_num(X_feat, nan=0.0, posinf=0.0, neginf=0.0)
        y_arr = np.array(y_trinx)
        
        for name, model in self.models.items():
            if "Deep Learning" in name or "trinx" in name: continue
            try:
                if isinstance(model, KNeighborsClassifier):
                    model.n_neighbors = min(5, len(X_feat))
                model.fit(X_feat, y_arr)
                tmp, fin = os.path.join(MODELS_DIR, f"{name}_TEMP.joblib"), os.path.join(MODELS_DIR, f"{name}.joblib")
                joblib.dump(model, tmp)
                os.replace(tmp, fin)
                self.model_status[name] = True 
            except Exception as e: print(f"Failed {name}: {e}")

        # 3. Keras Deep Learning
        self.root.after(0, lambda: self.lbl_ai_out.config(text="[ TRAINING DEEP LEARNING (PLEASE WAIT)... ]", fg="#ff00ff"))
        try:
            X_keras = pad_sequences(X_trinx_raw, maxlen=self.max_trinx_len, dtype='float32', padding='post', value=0.0)
            X_keras = X_keras.reshape((-1, self.max_trinx_len, 1))
            y_cat = to_categorical(y_arr, num_classes=len(self.labels_map))

            lstm = Sequential([
                Conv1D(64, 5, activation='relu', input_shape=(self.max_trinx_len, 1)),
                BatchNormalization(),
                MaxPooling1D(2),
                Dropout(0.3),
                Bidirectional(LSTM(64, return_sequences=True)),
                LSTM(32),
                Dense(len(self.labels_map), activation='softmax')
            ])
            lstm.compile(loss='categorical_crossentropy', optimizer=Adam(1e-3), metrics=['accuracy'])
            lstm.fit(X_keras, y_cat, epochs=40, batch_size=16, verbose=0)
            lstm.save(LSTM_MODEL_FILE)
            self.models["CNN-LSTM (Deep Learning)"] = lstm
            self.model_status["CNN-LSTM (Deep Learning)"] = True 

            gru = Sequential([
                Conv1D(64, 5, activation='relu', input_shape=(self.max_trinx_len, 1)),
                BatchNormalization(),
                MaxPooling1D(2),
                Dropout(0.3),
                Bidirectional(GRU(64, return_sequences=True)),
                GRU(32),
                Dense(len(self.labels_map), activation='softmax')
            ])
            gru.compile(loss='categorical_crossentropy', optimizer=Adam(1e-3), metrics=['accuracy'])
            gru.fit(X_keras, y_cat, epochs=40, batch_size=16, verbose=0)
            gru.save(GRU_MODEL_FILE)
            self.models["CNN-GRU (Deep Learning)"] = gru
            self.model_status["CNN-GRU (Deep Learning)"] = True 
        except Exception as e: print(f"DL Error: {e}")

        self.is_trained, self.is_training = True, False
        if self.model_status.get(self.active_model_name, False):
            self.root.after(0, lambda: self.lbl_ai_out.config(text=f"[ {self.active_model_name} READY ]", fg="#00ff00"))
        else:
            self.root.after(0, lambda: self.lbl_ai_out.config(text=f"[ ALL MODELS TRAINED ]", fg="#00ff00"))

    def toggle_prediction(self):
        if self.is_training: return
        self.is_predicting = not self.is_predicting
        if self.is_predicting: self.btn_predict.config(text="⏹ STOP PREDICTING", bg="#aa0000")
        else:
            self.btn_predict.config(text="▶ START PREDICTING", bg="#444")
            self.lbl_ai_out.config(text="[ STANDBY ]", fg="#aaaaaa")

    def predict_live_signal(self, full_live_buffer):
        if not self.model_status.get(self.active_model_name, False):
            self.lbl_ai_out.config(text=f"[ {self.active_model_name} UNTRAINED ]", fg="#ff4444")
            return
        try:
            # Grabs exactly the proper length from the end of the 4-second memory buffer
            live_trinx = full_live_buffer[-self.max_trinx_len:] 

            if "trinx" in self.active_model_name:
                idx, conf = self.models[self.active_model_name].predict(live_trinx)
            elif "Deep Learning" not in self.active_model_name:
                feats, _, _ = self.extract_features(live_trinx)
                probs = self.models[self.active_model_name].predict_proba([feats])
                idx, conf = int(np.argmax(probs)), float(np.max(probs)) * 100
            else:
                padded_live = pad_sequences([live_trinx], maxlen=self.max_trinx_len, dtype='float32', padding='post', value=0.0)
                probs = self.models[self.active_model_name].predict(padded_live.reshape((1, self.max_trinx_len, 1)), verbose=0)
                idx, conf = int(np.argmax(probs)), float(np.max(probs)) * 100

            if conf >= 90.0: 
                self.lbl_ai_out.config(text=f">> {self.labels_map[idx].upper()} ({conf:.1f}%) <<", fg="#00ffff")
            else: 
                rejected_word = self.labels_map[idx].upper()
                self.lbl_ai_out.config(text=f"[ REJECTED: {rejected_word} ({conf:.1f}%) ]", fg="#ffaa00")
        except Exception as e: print(e)

if __name__ == "__main__":
    app = QuantumSynapseGUI(tk.Tk())
    app.root.mainloop()
