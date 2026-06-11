import os
import json
import urllib.request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==============================================================================
# CONFIGURATION
# ==============================================================================
CITY = "Kochi"  # Change this to your preferred city name
SENDER_EMAIL = "adharshsaju.official@gmail.com"  # Replace with your Gmail address
RECEIVER_EMAIL = "adharshsaju.official@gmail.com"  # Where you want to get the alert
# ==============================================================================

def check_weather_and_alert():
    # Retrieve configuration variables securely from environment/GitHub secrets
    api_key = os.getenv("e4c51cea80c8d0274830a65f57d45769")
    email_password = os.getenv("tlhz tdnj opvb pqoi")
    
    if not api_key or not email_password:
        print("Missing API key or Email App Password configuration variables.")
        return

    # Fetch data using standard urllib setup
    url = f"https://api.github.com/data/2.5/weather?q={CITY}&appid={api_key}&units=metric"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching data from OpenWeatherMap: {e}")
        return

    # Extract critical target parameters
    temp = data["main"]["temp"]
    weather_condition = data["weather"][0]["main"].lower()
    weather_desc = data["weather"][0]["description"]

    print(f"Current weather in {CITY}: {temp}°C, {weather_desc}")

    # Evaluation conditions: Temp > 35°C OR Rain is predicted/occurring
    trigger_alert = False
    reason = ""

    if temp > 35:
        trigger_alert = True
        reason += f"• High temperature alert: The current temperature is {temp}°C (Exceeds 35°C).\n"
    if "rain" in weather_condition or "drizzle" in weather_condition:
        trigger_alert = True
        reason += f"• Precipitation alert: Rain detected condition matching standard: '{weather_desc}'.\n"

    # Send the email alert if conditions match
    if trigger_alert:
        print("Conditions met. Dispatching automated email alert...")
        send_email(temp, weather_desc, reason, email_password)
    else:
        print("Weather conditions are normal. No alert required.")

def send_email(temp, desc, reason, password):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"⚠️ WEATHER ALERT: Critical Conditions in {CITY}"

    body = f"""
    <h3>Weather Alert Notification System</h3>
    <p>Automated triggers have matched your threshold rules for <b>{CITY}</b>:</p>
    <div style="background: #fff5f5; border-left: 4px solid #e53e3e; padding: 10px; margin: 15px 0;">
        {reason.replace('\n', '<br>')}
    </div>
    <p><b>Current Status:</b> {temp}°C with {desc}.</p>
    <hr style="border:none; border-top:1px solid #eee;">
    <p style="font-size: 0.8rem; color: #777;">Sent automatically via GitHub Actions workflow container.</p>
    """
    
    msg.attach(MIMEText(body, 'html'))

    try:
        # Secure SMTP interface connection over Google core relay
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, password)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Alert email dispatched successfully.")
    except Exception as e:
        print(f"Failed to dispatch alert email protocol: {e}")

if __name__ == "__main__":
    check_weather_and_alert()