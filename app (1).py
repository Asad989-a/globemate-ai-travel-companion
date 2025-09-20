import gradio as gr
import requests
from transformers import pipeline
from deep_translator import GoogleTranslator

# -----------------------
# INIT
# -----------------------
try:
    chatbot = pipeline("text-generation", model="distilgpt2")
except Exception:
    chatbot = None

community_feed = []  # store shared tips

# -----------------------
# FUNCTIONS
# -----------------------
def chat_with_ai(query, language="English"):
    if not chatbot:
        return "⚠️ AI Model not loaded."
    try:
        response = chatbot(query, max_length=80, num_return_sequences=1)
        text = response[0].get("generated_text", "No response generated.")
        if language.lower() != "english":
            try:
                text = GoogleTranslator(source="en", target=language.lower()).translate(text)
            except Exception:
                text = f"(Partial English) {text}"
        return f"[{language}] {text}"
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


def convert_currency(amount, from_currency="USD", to_currency="PKR"):
    try:
        url = f"https://open.er-api.com/v6/latest/{from_currency.upper()}"
        res = requests.get(url, timeout=10).json()
        if res.get("result") == "success":
            rates = res.get("rates", {})
            if to_currency.upper() in rates:
                converted = round(float(amount) * rates[to_currency.upper()], 2)
                return f"{amount} {from_currency.upper()} = {converted} {to_currency.upper()}"
            else:
                return f"⚠️ Currency {to_currency.upper()} not supported."
        else:
            return f"⚠️ API Error: {res.get('error-type', 'Unknown error')}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def translate_text(text, lang="es"):
    try:
        return GoogleTranslator(source="auto", target=lang).translate(text)
    except Exception as e:
        return f"⚠️ Translation Error: {str(e)}"


def share_tip(user_tip):
    if user_tip.strip():
        community_feed.append(user_tip.strip())
    return "\n".join([f"• {tip}" for tip in community_feed[-10:]]) or "No tips shared yet."


def get_emergency_number(country):
    numbers = {
        "Pakistan": "Rescue 1122 / Police 15",
        "India": "112 (All emergencies)",
        "USA": "911",
        "UK": "999",
        "UAE": "999 (Police), 998 (Ambulance)"
    }
    return numbers.get(country, "⚠️ Not available, please check locally.")


def scam_detector(text):
    scam_keywords = ["lottery", "prize", "send money", "urgent transfer", "Nigerian prince"]
    if any(word in text.lower() for word in scam_keywords):
        return "⚠️ Potential Scam Detected!"
    return "✅ Message seems safe."


def lost_passport_help(country):
    return f"If you lost your passport in {country}, visit your embassy immediately and file a police report."


def carbon_calculator(distance_km, passengers=1):
    emissions = round(distance_km * passengers * 0.115, 2)
    return f"✈️ Estimated Carbon Footprint: {emissions} kg CO2"


def eco_hotels(city):
    eco_list = {
        "Karachi": ["Hotel One 🌱", "Pearl Eco Inn"],
        "Dubai": ["Green Oasis Hotel", "EcoPalm Resort"],
        "London": ["The Zetter Eco Hotel", "Green Stay Inn"],
    }
    return "\n".join(eco_list.get(city, ["⚠️ No eco-hotels found, try another city."]))


# -----------------------
# VOICE ASSISTANT
# -----------------------
def voice_assistant(audio_file):
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Pass recognized text to chatbot
        if chatbot:
            response = chatbot(text, max_length=80, num_return_sequences=1)
            reply = response[0].get("generated_text", "No response generated.")
            return f"🗣️ You said: {text}\n🤖 GlobeMate: {reply}"
        else:
            return "⚠️ AI Model not loaded."

    except Exception as e:
        return f"⚠️ Voice Assistant Error: {str(e)}"


# -----------------------
# IMAGE VIA URL
# -----------------------
def img_html(url, caption=""):
    return f"""
    <div style='text-align:center'>
        <img src="{url}" style='width:120px; border-radius:15px; margin:10px;'/>
        <p style='font-size:14px; color:gray'>{caption}</p>
    </div>
    """


# Example icons (from Flaticon)
travel_img = "https://cdn-icons-png.flaticon.com/512/69/69906.png"
currency_img = "https://cdn-icons-png.flaticon.com/512/2331/2331941.png"
translator_img = "https://cdn-icons-png.flaticon.com/512/2258/2258570.png"
community_img = "https://cdn-icons-png.flaticon.com/512/1256/1256650.png"
safety_img = "https://cdn-icons-png.flaticon.com/512/69/69906.png"
eco_img = "https://cdn-icons-png.flaticon.com/512/189/189001.png"
voice_img = "https://cdn-icons-png.flaticon.com/512/3602/3602145.png"

# -----------------------
# GRADIO UI
# -----------------------
def build_interface():
    with gr.Blocks(theme=gr.themes.Soft(), css="footer {display:none !important}") as demo:
        gr.HTML("<h1 style='text-align:center'>🌍 GlobeMate AI – Travel Companion</h1>")
        gr.HTML("<h3 style='text-align:center; color:gray'>✈️ Plan trips • 💱 Convert currency • 🛡️ Stay safe • 🌱 Travel green</h3>")

        # Travel Planner
        with gr.Tab("🤖 Travel Planner"):
            gr.HTML(img_html(travel_img, "AI Travel Planning"))
            query = gr.Textbox(label="Ask GlobeMate about your trip ✈️")
            lang = gr.Dropdown(["English", "Spanish", "French", "Urdu"], label="Language", value="English")
            out = gr.Textbox(label="AI Suggested Plan")
            btn = gr.Button("✨ Get Travel Plan")
            btn.click(chat_with_ai, [query, lang], out)

        # Currency
        with gr.Tab("💱 Currency Converter"):
            gr.HTML(img_html(currency_img, "Currency Conversion"))
            amount = gr.Number(label="Amount", value=1.0)
            from_cur = gr.Textbox(label="From Currency (e.g. USD)", value="USD")
            to_cur = gr.Textbox(label="To Currency (e.g. PKR)", value="PKR")
            result = gr.Textbox(label="Converted Amount")
            btn2 = gr.Button("💹 Convert")
            btn2.click(convert_currency, [amount, from_cur, to_cur], result)

        # Translator
        with gr.Tab("🌐 Translator"):
            gr.HTML(img_html(translator_img, "Live Translator"))
            text = gr.Textbox(label="Enter Text")
            lang_code = gr.Textbox(label="Target Language Code (e.g. es, fr, ur)", value="es")
            translated = gr.Textbox(label="Translated Text")
            btn4 = gr.Button("🌍 Translate")
            btn4.click(translate_text, [text, lang_code], translated)

        # Community
        with gr.Tab("👥 Community"):
            gr.HTML(img_html(community_img, "Traveler Tips"))
            tip_in = gr.Textbox(label="✍️ Share your travel tip")
            tip_out = gr.Textbox(label="🌏 Community Feed (last 10)")
            btn5 = gr.Button("📌 Post Tip")
            btn5.click(share_tip, [tip_in], tip_out)

        # Safety
        with gr.Tab("🛡️ Safety"):
            gr.HTML(img_html(safety_img, "Stay Safe"))
            country_in = gr.Textbox(label="Enter Country")
            emergency_out = gr.Textbox(label="🚨 Emergency Numbers")
            btn6 = gr.Button("📞 Get Emergency Number")
            btn6.click(get_emergency_number, [country_in], emergency_out)

            scam_in = gr.Textbox(label="Paste suspicious message")
            scam_out = gr.Textbox(label="🔍 Scam Detection Result")
            btn7 = gr.Button("🚫 Check Scam")
            btn7.click(scam_detector, [scam_in], scam_out)

            lost_in = gr.Textbox(label="Country where you lost passport")
            lost_out = gr.Textbox(label="🛂 Passport Help")
            btn8 = gr.Button("📖 Get Help")
            btn8.click(lost_passport_help, [lost_in], lost_out)

        # Eco Mode
        with gr.Tab("🌱 Eco Mode"):
            gr.HTML(img_html(eco_img, "Eco-Friendly Travel"))
            dist = gr.Number(label="Flight Distance (km)", value=1000)
            passengers = gr.Number(label="Passengers", value=1)
            carbon_out = gr.Textbox(label="🌍 Carbon Footprint")
            btn9 = gr.Button("🌱 Calculate Footprint")
            btn9.click(carbon_calculator, [dist, passengers], carbon_out)

            eco_city = gr.Textbox(label="Enter City")
            eco_out = gr.Textbox(label="🏨 Eco Hotels")
            btn10 = gr.Button("🍀 Find Eco Hotels")
            btn10.click(eco_hotels, [eco_city], eco_out)

        # Voice Assistant
        with gr.Tab("🎤 Voice Assistant"):
            gr.HTML(img_html(voice_img, "Talk to GlobeMate"))
            voice_in = gr.Audio(label="🎤 Speak now (record) — press STOP to send", format="wav")
            voice_out = gr.Textbox(label="Voice Assistant Response")
            voice_btn = gr.Button("🎙️ Process Voice")
            voice_btn.click(voice_assistant, [voice_in], voice_out)

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch()
