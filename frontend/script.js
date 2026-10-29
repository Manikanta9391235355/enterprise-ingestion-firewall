
const API = "";

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const sessionLabel = document.getElementById("sessionLabel");
const connectionStatus = document.getElementById("connectionStatus");
const errorBox = document.getElementById("errorBox");

let sessionId = null;
let isLoading = false;

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function setLoading(value) {
  isLoading = value;
  sendBtn.disabled = value;
  newChatBtn.disabled = value;
  messageInput.disabled = value;
  sendBtn.textContent = value ? "Sending..." : "Send";
}

function updateSessionLabel() {
  sessionLabel.textContent = sessionId
    ? sessionId.slice(0, 8) + "..."
    : "Not started";
}

function clearMessages() {
  chatMessages.replaceChildren();

  const welcome = document.createElement("div");
  welcome.className = "welcome";
  welcome.id = "welcome";

  const icon = document.createElement("div");
  icon.className = "welcome-icon";
  icon.textContent = "✦";

  const heading = document.createElement("h1");
  heading.textContent = "How can I help you today?";

  const description = document.createElement("p");
  description.textContent =
    "Ask about billing, technical support, or general questions.";

  welcome.append(icon, heading, description);
  chatMessages.appendChild(welcome);
}

function appendMessage(role, content) {
  document.getElementById("welcome")?.remove();

  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "U" : "AI";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (
    role === "assistant" &&
    window.marked &&
    window.DOMPurify
  ) {
    const html = marked.parse(content);
    bubble.innerHTML = DOMPurify.sanitize(html);
  } else {
    bubble.textContent = content;
  }

  wrapper.append(avatar, bubble);
  chatMessages.appendChild(wrapper);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  return wrapper;
}

function showLoading() {
  const loading = document.createElement("div");
  loading.id = "loadingIndicator";
  loading.className = "loading";

  const spinner = document.createElement("span");
  spinner.className = "spinner";

  const text = document.createElement("span");
  text.textContent = "Analyzing your message...";

  loading.append(spinner, text);
  chatMessages.appendChild(loading);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoading() {
  document.getElementById("loadingIndicator")?.remove();
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API}${path}`, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : `Request failed (${response.status})`
    );
  }

  return data;
}

async function createSession() {
  const data = await apiRequest("/sessions", {
    method: "POST",
  });

  sessionId = data.session_id;
  updateSessionLabel();

  return sessionId;
}

async function newChat() {
  if (isLoading) return;

  setLoading(true);
  clearError();

  try {
    await createSession();
    clearMessages();
    clearInsights();
    messageInput.value = "";
  } catch (error) {
    showError(error.message);
  } finally {
    setLoading(false);
  }
}

function updateInsights(firewall) {
  document.getElementById("emptyInsights")
    .classList.add("hidden");

  document.getElementById("insightResults")
    .classList.remove("hidden");

  document.getElementById("intentValue").textContent =
    firewall.intent.category;

  document.getElementById("confidenceValue").textContent =
    `Confidence: ${Math.round(
      firewall.intent.confidence * 100
    )}%`;

  document.getElementById("riskValue").textContent =
    firewall.risk.level;

  document.getElementById("riskReason").textContent =
    firewall.risk.reason;

  document.getElementById("priorityValue").textContent =
    firewall.priority.level;

  document.getElementById("priorityScore").textContent =
    `Score: ${firewall.priority.score}/10`;

  document.getElementById("totalTokens").textContent =
    firewall.tokens.total_tokens;

  document.getElementById("tokenDetails").textContent =
    `Input: ${firewall.tokens.input_tokens} | ` +
    `Output: ${firewall.tokens.output_tokens}`;
}

function clearInsights() {
  document.getElementById("emptyInsights")
    .classList.remove("hidden");

  document.getElementById("insightResults")
    .classList.add("hidden");
}

async function sendMessage(event) {
  event.preventDefault();

  const text = messageInput.value.trim();

  if (!text || isLoading) return;

  clearError();
  setLoading(true);
  messageInput.value = "";

  const userBubble = appendMessage("user", text);
  showLoading();

  try {
    if (!sessionId) {
      await createSession();
    }

    const data = await apiRequest("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: text,
      }),
    });

    removeLoading();
    appendMessage("assistant", data.response);
    updateInsights(data.firewall);

  } catch (error) {
    removeLoading();
    userBubble.remove();
    messageInput.value = text;
    showError(error.message);
  } finally {
    setLoading(false);
    messageInput.focus();
  }
}

async function checkBackend() {
  try {
    const data = await apiRequest("/health");

    connectionStatus.textContent =
      data.status === "healthy"
        ? "Backend connected"
        : "Backend responding";
  } catch {
    connectionStatus.textContent = "Backend disconnected";
  }
}

chatForm.addEventListener("submit", sendMessage);
newChatBtn.addEventListener("click", newChat);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();

    if (!isLoading) {
      chatForm.requestSubmit();
    }
  }
});

document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.message;
    messageInput.focus();
  });
});

checkBackend();
updateSessionLabel();
