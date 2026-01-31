CureVox

Multilingual AI-Based Health Guidance System

📌 Project Overview

CureVox is a secure, multilingual AI-based health guidance system designed to support early health awareness through non-invasive user inputs. The platform enables users to interact using text or voice, answer guided follow-up questions, and receive clear, ethical health guidance focused on awareness and prevention.

CureVox does not diagnose diseases and does not prescribe medicines. Instead, it helps users understand whether a condition appears normal or requires further medical attention, while responsibly encouraging professional consultation when necessary.

🎯 Problem Statement

Many people delay seeking medical help due to uncertainty, accessibility issues, or language barriers. Existing digital health tools are often diagnosis-focused, complex, or inaccessible to non-technical users.

There is a need for a simple, multilingual, and ethical health guidance system that supports early understanding without replacing healthcare professionals.


💡 Solution

CureVox provides:

Guided health interaction through voice and text

User-selected health guidance modes

Interactive symptom-based conversation

Ethical conclusions focused on awareness and prevention

Responsible escalation to nearby medical professionals when required

The system acts as a pre-consultation health assistant, not a diagnostic tool.


🔄 How CureVox Works

User securely logs in

User selects the type of guidance:

General health guidance (based on cough and breathing sounds)

Rash guidance (based on skin images)

User provides the required input

The system initiates an interactive conversational flow

Relevant follow-up questions are asked

A clear and ethical conclusion is generated

Natural and home-based care suggestions are provided

Nearby doctors are suggested if required

A downloadable health summary report is generated


🌍 Key Features

Multilingual interaction

Voice-enabled and text-based conversation

User-controlled guidance selection

Interactive symptom discussion

Natural and home-based care guidance

Location-aware doctor recommendations

Privacy-first data handling

Downloadable health summary report


🛡️ Ethics & Safety

CureVox strictly follows responsible healthcare principles:

❌ No disease diagnosis

❌ No medicine prescription

✅ Awareness and guidance only

✅ Encourages professional consultation when necessary

The platform is designed to support, not replace, medical professionals.


🔐 Privacy & Data Handling

Secure authentication

No permanent storage of audio or image data

Sensitive credentials are excluded from the repository

Configuration is handled through environment variables


📁 Project Structure
CureVox/
├── backend/
├── frontend/
├── docker/
├── scripts/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore


⚙️ Setup & Installation
Prerequisites :

Python 3.x installed

pip package manager

Internet connection for dependency installation


Quick Execution : 


Navigate to backend directory
cd curevox-main/backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
cp .env.example .env           # Create .env File (Local Only), Copy the example file : cp .env.example .env , Update .env with your own local credentials
python app.py


The application will start at:

http://localhost:5000


📄 Reports

After completing a guidance session, users can download a health summary report containing:

Guidance overview

Conversational insights

Ethical conclusion

Recommendations


💼 Business Model – CureVox

CureVox follows an affordable, pay-per-use healthcare guidance model, ensuring accessibility while maintaining long-term sustainability. Each session provides complete value, covering guided conversational interaction, analysis, and downloadable health report generation.

🔹 Service Pricing (All-Inclusive)

General Health Guidance (Cough & Breathing)
₹30 – ₹50 per session
(Includes chatbot interaction, analysis, and health summary report)

Rash Guidance (Skin Image Analysis)
₹25 – ₹40 per session
(Includes chatbot interaction, analysis, and health summary report)

This transparent pricing avoids subscriptions and hidden charges, encouraging users to seek early guidance without financial hesitation.


📌 Disclaimer

CureVox is an AI-based health guidance system intended for informational and awareness purposes only. It does not provide medical diagnosis or treatment. Users should consult qualified healthcare professionals for medical decisions.



👥 Team CureVox

Hari S
Dharaneesh M
Sarvesh K
Ajay V


Department of Electronics Engineering


Madras Institute of Technology


Chennai, Tamil Nadu, India
