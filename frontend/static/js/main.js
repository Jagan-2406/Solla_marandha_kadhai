// Global variables to store current generated results and state
let currentResultText = "";
let isAudioPlaying = false;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  setupTheme();
  setupEventListeners();
});

// Theme Toggle Logic
function setupTheme() {
  const themeToggle = document.getElementById("theme-toggle");
  const storedTheme = localStorage.getItem("theme");

  if (storedTheme === "light") {
    document.body.classList.remove("dark-mode");
    document.body.classList.add("light-mode");
  } else {
    document.body.classList.remove("light-mode");
    document.body.classList.add("dark-mode");
  }

  themeToggle.addEventListener("click", () => {
    if (document.body.classList.contains("dark-mode")) {
      document.body.classList.remove("dark-mode");
      document.body.classList.add("light-mode");
      localStorage.setItem("theme", "light");
    } else {
      document.body.classList.remove("light-mode");
      document.body.classList.add("dark-mode");
      localStorage.setItem("theme", "dark");
    }
  });
}

function setupEventListeners() {
  // Input animation effect on load/focus
  const inputs = document.querySelectorAll("input[type='text'], select");
  inputs.forEach(input => {
    input.addEventListener("focus", () => {
      input.parentElement.classList.add("active");
    });
    input.addEventListener("blur", () => {
      input.parentElement.classList.remove("active");
    });
  });
}

// Preset Handler
function applyPreset(noun, verb, tense, gender, sentType) {
  document.getElementById("noun").value = noun;
  document.getElementById("verb").value = verb;
  document.getElementById("tense").value = tense;
  document.getElementById("gender").value = gender;
  document.getElementById("sentence_type").value = sentType;
  
  // Highlight elements briefly to show they changed
  const inputs = ["noun", "verb", "tense", "gender", "sentence_type"];
  inputs.forEach(id => {
    const el = document.getElementById(id);
    el.style.transform = "scale(1.03)";
    setTimeout(() => { el.style.transform = "none"; }, 200);
  });
}

// Generate Tamil Sentence API Request
async function generateSentence() {
  const noun = document.getElementById("noun").value.trim();
  const verb = document.getElementById("verb").value.trim();
  const tense = document.getElementById("tense").value;
  const gender = document.getElementById("gender").value;
  const sentenceType = document.getElementById("sentence_type").value;

  if (!noun || !verb) {
    alert("தயவுசெய்து பெயர்ச்சொல் மற்றும் வினைச்சொல்லை உள்ளிடவும். (Please enter both noun and verb.)");
    return;
  }

  // Update button and status to loading state
  const submitBtn = document.getElementById("submit-btn");
  const statusBadge = document.getElementById("status-badge");
  submitBtn.disabled = true;
  submitBtn.style.opacity = "0.7";
  statusBadge.textContent = "உருவாக்குகிறது... (Generating...)";
  statusBadge.style.color = "#fbbf24";
  statusBadge.style.borderColor = "rgba(251, 191, 36, 0.2)";

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        noun: noun,
        verb: verb,
        tense: tense,
        gender: gender,
        sentence_type: sentenceType
      })
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.error || "Failed to generate");
    }

    const data = await response.json();
    displayResults(data, noun, verb, tense, gender);
    
    // Reset status to Success
    statusBadge.textContent = "வெற்றி (Success)";
    statusBadge.style.color = "#10b981";
    statusBadge.style.borderColor = "rgba(16, 185, 129, 0.2)";
  } catch (error) {
    console.error("Error:", error);
    alert(`Error: ${error.message}`);
    statusBadge.textContent = "பிழை (Error)";
    statusBadge.style.color = "#ef4444";
    statusBadge.style.borderColor = "rgba(239, 68, 68, 0.2)";
  } finally {
    submitBtn.disabled = false;
    submitBtn.style.opacity = "1";
  }
}

// Display results based on response types
function displayResults(data, noun, verb, tense, gender) {
  const placeholder = document.getElementById("result-placeholder");
  const singleCard = document.getElementById("single-result-card");
  const dialogueCard = document.getElementById("dialogue-result-card");

  // Hide placeholder
  placeholder.classList.add("hidden");

  // Format a friendly English structural breakdown for learning
  const breakdown = getBreakdownString(noun, verb, tense, gender, data.type);

  if (data.type === "statement" || data.type === "question") {
    // Show single result card
    dialogueCard.classList.add("hidden");
    singleCard.classList.remove("hidden");

    currentResultText = data.output;
    document.getElementById("output-text-tamil").textContent = data.output;
    document.getElementById("output-text-translation").textContent = breakdown;
  } else if (data.type === "dialogue") {
    // Show dialogue card
    singleCard.classList.add("hidden");
    dialogueCard.classList.remove("hidden");

    const bubblesContainer = document.getElementById("chat-bubbles-container");
    bubblesContainer.innerHTML = ""; // Clear existing bubbles

    data.output.forEach((dialogueLine, idx) => {
      // Determine side: Friend (நண்பன்) is Left, Subject (அவன், நான், etc.) is Right
      const isFriend = dialogueLine.speaker === "நண்பன்";
      const bubbleSide = isFriend ? "left" : "right";
      const avatarInitial = isFriend ? "ந" : dialogueLine.speaker.charAt(0);
      
      const bubbleHTML = `
        <div class="chat-bubble ${bubbleSide}" style="animation-delay: ${idx * 0.2}s">
          <div class="avatar">${avatarInitial}</div>
          <div class="bubble-content">
            <div class="bubble-speaker">${dialogueLine.speaker}</div>
            <div class="bubble-text">${dialogueLine.line}</div>
            <div class="bubble-actions">
              <button class="bubble-speak-btn" onclick="speakText('${dialogueLine.line.replace(/'/g, "\\'")}', this)" title="Listen">
                <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                  <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      `;
      bubblesContainer.insertAdjacentHTML("beforeend", bubbleHTML);
    });
  }
}

// Generate human-friendly structural breakdown
function getBreakdownString(noun, verb, tense, gender, type) {
  const tenses = { present: "Present Tense", past: "Past Tense", future: "Future Tense" };
  const genders = {
    first: "First Person ('I')",
    male: "Masculine ('He')",
    female: "Feminine ('She')",
    neutral: "Neutral ('It')",
    plural: "Plural/Honorific ('They')"
  };
  const typeLabel = type === "question" ? "Question" : "Statement";
  
  return `Structure: [Subject: ${genders[gender]}] + [Noun: ${noun}] + [Verb Root: ${verb}] + [Tense Suffix: ${tenses[tense]}] = ${typeLabel}`;
}

// Call Text-to-Speech endpoint and play audio
function speakResultText() {
  const mainSpeakBtn = document.getElementById("main-speak-btn");
  speakText(currentResultText, mainSpeakBtn);
}

async function speakText(text, buttonElement) {
  if (isAudioPlaying) return;
  if (!text) return;

  isAudioPlaying = true;
  buttonElement.classList.add("speaking");
  
  // Visual Feedback: modify icon or text of the button
  const originalHTML = buttonElement.innerHTML;
  
  try {
    const response = await fetch("/tts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: text })
    });

    if (!response.ok) {
      throw new Error("Failed to load TTS audio");
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    
    const audioEl = document.getElementById("tts-audio-element");
    audioEl.src = audioUrl;
    
    audioEl.onplay = () => {
      // Rotate/pulse icon animation (handled by CSS when .speaking is active)
    };

    audioEl.onended = () => {
      buttonElement.classList.remove("speaking");
      buttonElement.innerHTML = originalHTML;
      URL.revokeObjectURL(audioUrl);
      isAudioPlaying = false;
    };
    
    audioEl.onerror = () => {
      throw new Error("Audio playback error");
    };

    await audioEl.play();
  } catch (error) {
    console.error("Audio error:", error);
    buttonElement.classList.remove("speaking");
    buttonElement.innerHTML = originalHTML;
    isAudioPlaying = false;
    alert("Audio playback failed.");
  }
}
