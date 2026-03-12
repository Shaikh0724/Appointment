const messagesEl = document.getElementById("chatMessages");
const inputEl = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const stopVoiceBtn = document.getElementById("stopVoiceBtn");
const statusText = document.getElementById("statusText");
const autoSpeakEl = document.getElementById("autoSpeak");
const newChatBtn = document.getElementById("newChatBtn");

const CHAT_API = "/chat";
const SESSION_KEY = "smilebot_session_id";

const sessionId = localStorage.getItem(SESSION_KEY) || generateSessionId();
localStorage.setItem(SESSION_KEY, sessionId);

let recognition = null;
let listening = false;

function generateSessionId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.floor(Math.random() * 100000)}`;
}

function addMessage(role, text) {
  const item = document.createElement("div");
  item.className = `msg ${role}`;
  item.textContent = text;
  messagesEl.appendChild(item);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setStatus(text) {
  statusText.textContent = text;
}

function setLoading(state) {
  sendBtn.disabled = state;
  micBtn.disabled = state && !listening;
}

async function sendMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) {
    return;
  }

  addMessage("user", trimmed);
  inputEl.value = "";
  autoResizeInput();
  setLoading(true);
  setStatus("Thinking...");

  try {
    const res = await fetch(CHAT_API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: trimmed,
      }),
    });

    if (!res.ok) {
      throw new Error(`Request failed with status ${res.status}`);
    }

    const data = await res.json();
    const reply = data.reply || "Sorry, I could not generate a response right now.";
    addMessage("bot", reply);

    if (data.booking_captured) {
      addMessage(
        "system",
        "Appointment details captured successfully. Samantha will follow up to confirm the exact time."
      );
    }

    if (autoSpeakEl.checked) {
      speakText(reply);
    }

    setStatus("Ready");
  } catch (err) {
    addMessage(
      "system",
      "I am having trouble connecting right now. Please call 1-910-347-9100 for immediate help."
    );
    setStatus("Connection issue");
    console.error(err);
  } finally {
    setLoading(false);
  }
}

function autoResizeInput() {
  inputEl.style.height = "auto";
  inputEl.style.height = `${Math.min(inputEl.scrollHeight, 140)}px`;
}

function speakText(text) {
  if (!("speechSynthesis" in window)) {
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1.05;
  utterance.lang = "en-US";

  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(
    (v) => v.lang.startsWith("en") && /female|samantha|zira|aria|google us english/i.test(v.name)
  );
  if (preferred) {
    utterance.voice = preferred;
  }

  window.speechSynthesis.speak(utterance);
}

function stopSpeaking() {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
}

function configureVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    micBtn.disabled = true;
    micBtn.textContent = "Voice N/A";
    setStatus("Voice input unsupported in this browser");
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onstart = () => {
    listening = true;
    micBtn.classList.add("listening");
    micBtn.textContent = "Listening...";
    setStatus("Listening");
  };

  recognition.onend = () => {
    listening = false;
    micBtn.classList.remove("listening");
    micBtn.textContent = "Speak";
    setStatus("Ready");
  };

  recognition.onerror = () => {
    setStatus("Voice input error");
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    inputEl.value = transcript;
    autoResizeInput();
    sendMessage(transcript);
  };
}

sendBtn.addEventListener("click", () => sendMessage(inputEl.value));

inputEl.addEventListener("input", autoResizeInput);
inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage(inputEl.value);
  }
});

micBtn.addEventListener("click", () => {
  if (!recognition) {
    return;
  }
  if (listening) {
    recognition.stop();
    return;
  }
  recognition.start();
});

stopVoiceBtn.addEventListener("click", stopSpeaking);

newChatBtn.addEventListener("click", () => {
  stopSpeaking();
  messagesEl.innerHTML = "";
  const newSession = generateSessionId();
  localStorage.setItem(SESSION_KEY, newSession);
  addMessage(
    "system",
    "Started a new chat session. You can ask about services or request an appointment."
  );
});

window.speechSynthesis?.addEventListener?.("voiceschanged", () => {
  // Triggers loading available voices in some browsers.
});

configureVoiceInput();
autoResizeInput();
addMessage(
  "bot",
  "Hi! I am SmileBot from A Beautiful Smile. How can I help you today?"
);
