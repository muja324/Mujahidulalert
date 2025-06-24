import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import requests
import smtplib
from email.mime.text import MIMEText
import matplotlib.pyplot as plt

# ------------------- SETTINGS -------------------
st.title("📈 Trading Alert Dashboard – by Mujahidul")

symbol = st.text_input("🔍 Stock Symbol", "ASTERDM.NS")
breakout_level = st.number_input("📈 Breakout Level", value=575.0)
breakdown_level = st.number_input("📉 Breakdown Level", value=560.0)
fakeout_sensitivity = st.slider("🎯 Fakeout Sensitivity", 1.0, 5.0, 2.5)
lookback = st.slider("🕒 Lookback Candles", 50, 200, 100)

notify_option = st.selectbox("🔔 Alert Method", ["In-App Only", "Telegram", "Email"])

# Telegram config
bot_token = st.text_input("🤖 7934586337:AAGTBfUruRDbB1M4HKlBsf1C3FdZpdgJJIE", "")
chat_id = st.text_input("💬 689374593", "")

# Email config
email_to = st.text_input("📧 Alert Email", "")
email_from = "imujahid788@gmail.com"
app_password = st.text_input("Mujahid1#", "", type="password")

# ------------------- DATA FETCH -------------------
try:
    df = yf.download(symbol, period='5d', interval='15m')
    df['Range'] = df['High'] - df['Low']
    df['Body'] = abs(df['Close'] - df['Open'])
    df['Trap'] = np.where((df['Range'] > df['Body'] * fakeout_sensitivity), 1, 0)
    latest_price = df['Close'].iloc[-1]
    st.metric("📌 Current Price", f"{latest_price:.2f}")
except Exception as e:
    st.error("❌ Error fetching stock data.")
    st.stop()

# ------------------- ALERT LOGIC -------------------
def send_telegram(msg):
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": msg})

def send_email(msg):
    if email_to and app_password:
        message = MIMEText(msg)
        message["Subject"] = "Stock Alert – Trap/Breakout"
        message["From"] = email_from
        message["To"] = email_to
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_from, app_password)
        server.sendmail(email_from, email_to, message.as_string())
        server.quit()

# Trigger Zones
if latest_price > breakout_level:
    msg = f"🚀 Breakout Alert: {symbol} above {breakout_level} @ {latest_price:.2f}"
    st.success(msg)
elif latest_price < breakdown_level:
    msg = f"🔻 Breakdown Alert: {symbol} below {breakdown_level} @ {latest_price:.2f}"
    st.error(msg)
else:
    msg = "🕒 Waiting for breakout or breakdown zone..."

trap_zones = df.tail(lookback)[df['Trap'] == 1]
if not trap_zones.empty:
    st.warning(f"⚠️ {len(trap_zones)} Trap Zones detected recently.")

# Notification
if notify_option != "In-App Only":
    if "Alert" in msg:
        if notify_option == "Telegram":
            send_telegram(msg)
        elif notify_option == "Email":
            send_email(msg)

# ------------------- PLOT -------------------
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df['Close'], label='Close Price', color='blue')
ax.scatter(trap_zones.index, trap_zones['Close'], color='red', label='Trap Zones')
ax.axhline(y=breakout_level, color='green', linestyle='--', label='Breakout Level')
ax.axhline(y=breakdown_level, color='orange', linestyle='--', label='Breakdown Level')
ax.set_title(f"{symbol} – Price Chart with Trap Zones")
ax.legend()
st.pyplot(fig)
