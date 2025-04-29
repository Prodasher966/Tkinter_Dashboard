# Crime Dashboard in Tkinter using Plotly, Matplotlib, Seaborn, and Pandas

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import datetime as dt

# Load and preprocess data
data = pd.read_csv("Crime_Data_from_2020_to_Present.csv", parse_dates=['DATE OCC'], low_memory=False)
data = data.dropna(subset=['LAT', 'LON'])
data = data.dropna(subset=['Vict Age'])
data['Vict Age'] = pd.to_numeric(data['Vict Age'], errors='coerce')
data = data.dropna(subset=['Vict Age'])
data['Vict Age'] = data['Vict Age'].astype(int)

# Helper functions
def filter_data():
    filtered = data.copy()
    try:
        start = pd.to_datetime(start_date.get())
        end = pd.to_datetime(end_date.get())
        filtered = filtered[(filtered['DATE OCC'] >= start) & (filtered['DATE OCC'] <= end)]

        if area_var.get() != "All":
            filtered = filtered[filtered['AREA NAME'] == area_var.get()]
        if crime_var.get() != "All":
            filtered = filtered[filtered['Crm Cd Desc'] == crime_var.get()]
        if outcome_var.get() != "All":
            filtered = filtered[filtered['Status Desc'] == outcome_var.get()]

        min_age, max_age = age_slider.get(), age_slider2.get()
        filtered = filtered[(filtered['Vict Age'] >= min_age) & (filtered['Vict Age'] <= max_age)]
    except Exception as e:
        print("Filter error:", e)
    return filtered

def threaded_plot(func):
    threading.Thread(target=func).start()

def show_trend():
    filtered = filter_data()
    df = filtered.groupby(filtered['DATE OCC'].dt.to_period('M')).size().reset_index(name='Crimes')
    df['DATE OCC'] = df['DATE OCC'].dt.to_timestamp()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=df, x='DATE OCC', y='Crimes', ax=ax)
    ax.set_title("📈 Crime Trends Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Crimes")
    fig.suptitle("Line graph showing crime frequency over time based on selected filters.", fontsize=10)
    show_plot(fig)

def show_top_crimes():
    filtered = filter_data()
    df = filtered['Crm Cd Desc'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=df.values, y=df.index, ax=ax, palette='magma')
    ax.set_title("🔝 Top 10 Crime Types")
    ax.set_xlabel("Number of Crimes")
    ax.set_ylabel("Crime Type")
    fig.suptitle("Bar chart of the top 10 most frequent crimes.", fontsize=10)
    show_plot(fig)

def show_by_area():
    filtered = filter_data()
    df = filtered['AREA NAME'].value_counts().reset_index()
    df.columns = ['Area', 'Count']
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, y='Area', x='Count', palette='coolwarm', ax=ax)
    ax.set_title("📍 Crime Count by Area")
    ax.set_xlabel("Number of Crimes")
    ax.set_ylabel("Area")
    fig.tight_layout()
    fig.suptitle("Bar chart showing total number of crimes by area.", fontsize=10, y=1.02)
    show_plot(fig)

def show_time_heatmap():
    filtered = filter_data()
    filtered['Hour'] = filtered['TIME OCC'] // 100
    filtered['Weekday'] = filtered['DATE OCC'].dt.day_name()
    heatmap_data = pd.crosstab(filtered['Hour'], filtered['Weekday'])
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax)
    ax.set_title("⏰ Crimes by Hour and Weekday")
    fig.suptitle("Heatmap showing crime density by hour and weekday.", fontsize=10)
    show_plot(fig)

def show_outcomes():
    filtered = filter_data()
    df = filtered['Status Desc'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=df.values, y=df.index, ax=ax)
    ax.set_title("Crime Outcomes (Count by Status)")
    ax.set_xlabel("Number of Crimes")
    ax.set_ylabel("Outcome Type")
    fig.tight_layout()
    show_plot(fig)


def show_victim_demographics():
    filtered = filter_data()
    fig, axs = plt.subplots(1, 3, figsize=(15, 4))

    # Victim Sex - Bar
    sex_counts = filtered['Vict Sex'].value_counts()
    sns.barplot(x=sex_counts.index, y=sex_counts.values, ax=axs[0])
    axs[0].set_title("Victim Sex Distribution")
    axs[0].set_ylabel("Count")

    # Age - Line plot with bins
    age_bins = pd.cut(filtered['Vict Age'], bins=[0, 18, 30, 45, 60, 100])
    age_counts = age_bins.value_counts().sort_index()
    axs[1].plot(age_counts.index.astype(str), age_counts.values, marker='o')
    axs[1].set_title("Victim Age Ranges")
    axs[1].set_ylabel("Count")
    axs[1].tick_params(axis='x', rotation=45)

    # Descent - Bar
    descent_counts = filtered['Vict Descent'].value_counts().head(10)
    sns.barplot(x=descent_counts.index, y=descent_counts.values, ax=axs[2])
    axs[2].set_title("Top 10 Victim Descent Groups")
    axs[2].set_ylabel("Count")
    axs[2].tick_params(axis='x', rotation=45)

    fig.tight_layout()
    show_plot(fig)


def show_weapon_types():
    filtered = filter_data()
    df = filtered['Weapon Desc'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=df.values, y=df.index, ax=ax, palette='viridis')
    ax.set_title("🔫 Top Weapon Types")
    ax.set_xlabel("Occurrences")
    ax.set_ylabel("Weapon")
    fig.suptitle("Bar chart of most commonly reported weapons used in crimes.", fontsize=10)
    show_plot(fig)


def show_plot(fig):
    for widget in plot_frame.winfo_children():
        widget.destroy()
    fig.tight_layout()  # Adjusts spacing to prevent clipping
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# Tkinter App Setup
root = tk.Tk()
root.title("L.A. Crime Data Dashboard")
root.geometry("1200x800")

control_frame = tk.Frame(root)
control_frame.pack(pady=10)

# Filters
tk.Label(control_frame, text="Start Date").grid(row=0, column=0)
start_date = DateEntry(control_frame)
start_date.set_date(dt.date(2020, 1, 1))
start_date.grid(row=0, column=1)

tk.Label(control_frame, text="End Date").grid(row=0, column=2)
end_date = DateEntry(control_frame)
end_date.set_date(dt.date.today())
end_date.grid(row=0, column=3)

area_var = tk.StringVar(value="All")
crime_var = tk.StringVar(value="All")
outcome_var = tk.StringVar(value="All")

tk.Label(control_frame, text="Area").grid(row=1, column=0)
tt = ttk.Combobox(control_frame, textvariable=area_var, values=["All"] + sorted(data['AREA NAME'].dropna().unique().tolist()))
tt.grid(row=1, column=1)

tk.Label(control_frame, text="Crime Type").grid(row=1, column=2)
tt2 = ttk.Combobox(control_frame, textvariable=crime_var, values=["All"] + sorted(data['Crm Cd Desc'].dropna().unique().tolist()))
tt2.grid(row=1, column=3)

tk.Label(control_frame, text="Outcome").grid(row=1, column=4)
tt3 = ttk.Combobox(control_frame, textvariable=outcome_var, values=["All"] + sorted(data['Status Desc'].dropna().unique().tolist()))
tt3.grid(row=1, column=5)

# Sliders
age_slider = tk.Scale(control_frame, from_=0, to=100, label="Min Age", orient=tk.HORIZONTAL)
age_slider.set(0)
age_slider.grid(row=2, column=0, columnspan=2)

age_slider2 = tk.Scale(control_frame, from_=0, to=100, label="Max Age", orient=tk.HORIZONTAL)
age_slider2.set(100)
age_slider2.grid(row=2, column=2, columnspan=2)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack()

buttons = [
    ("Crime Trend", lambda: threaded_plot(show_trend)),
    ("Top Crimes", lambda: threaded_plot(show_top_crimes)),
    ("By Area", lambda: threaded_plot(show_by_area)),
    ("Time Heatmap", lambda: threaded_plot(show_time_heatmap)),
    ("Outcomes", lambda: threaded_plot(show_outcomes)),
    ("Demographics", lambda: threaded_plot(show_victim_demographics)),
    ("Weapons", lambda: threaded_plot(show_weapon_types)),
]

for i, (text, cmd) in enumerate(buttons):
    b = tk.Button(btn_frame, text=text, command=cmd)
    b.grid(row=0, column=i, padx=5, pady=10)

plot_frame = tk.Frame(root)
plot_frame.pack(expand=True, fill=tk.BOTH)

root.mainloop()
