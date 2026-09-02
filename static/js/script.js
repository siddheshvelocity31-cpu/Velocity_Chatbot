// ============================================
// SEND MESSAGE
// ============================================

async function sendMessage() {

    const input = document.getElementById("messageInput");
    const message = input.value.trim();

    if (!message) {
        return;
    }

    input.value = "";

    addMessage("user", message);

    showTyping();

    const button = document.getElementById("sendButton");
    button.disabled = true;

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });

        const data = await response.json();

        removeTyping();

        if (data.success) {

            addMessage(
                "assistant",
                data.response,
                data.tools
            );

        } else {

            addMessage(
                "assistant",
                "❌ Error: " + data.error
            );

        }

        loadHistory();

    } catch (error) {

        removeTyping();

        addMessage(
            "assistant",
            "❌ Could not connect to the Flask server."
        );

        console.error(error);

    }

    button.disabled = false;

    input.focus();
}


// ============================================
// ADD MESSAGE
// ============================================

function addMessage(role, text, tools = []) {

    const chat = document.getElementById("chat");

    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }

    const message = document.createElement("div");

    message.className =
        "message " +
        (role === "user"
            ? "user-message"
            : "assistant-message");


    const avatar =
        role === "user"
            ? "🧑‍💻"
            : "🤖";


    const name =
        role === "user"
            ? "You"
            : "Gemini";


    let toolsHTML = "";

    if (tools && tools.length > 0) {

        toolsHTML = `
            <div style="
                margin-top:12px;
                padding:10px;
                background:#f5f7fa;
                border-radius:10px;
                font-size:12px;
            ">
                ⚙️ ${tools.length} tool event(s) executed
            </div>
        `;

    }


    message.innerHTML = `

        <div class="avatar">
            ${avatar}
        </div>

        <div class="message-content">

            <div class="message-name">
                ${name}
            </div>

            <div class="message-text">
                ${escapeHTML(text)}
            </div>

            ${toolsHTML}

        </div>
    `;


    chat.appendChild(message);

    scrollToBottom();
}


// ============================================
// TYPING INDICATOR
// ============================================

function showTyping() {

    const chat = document.getElementById("chat");

    const typing = document.createElement("div");

    typing.id = "typing";

    typing.className =
        "message assistant-message";

    typing.innerHTML = `

        <div class="avatar">
            🤖
        </div>

        <div class="message-content">

            <div class="message-name">
                Gemini
            </div>

            <div class="typing">
                Gemini is thinking...
            </div>

        </div>
    `;

    chat.appendChild(typing);

    scrollToBottom();
}


function removeTyping() {

    const typing =
        document.getElementById("typing");

    if (typing) {
        typing.remove();
    }
}


// ============================================
// NEW CHAT
// ============================================

async function newChat() {

    await fetch("/new-chat", {
        method: "POST"
    });

    document.getElementById("chat").innerHTML = `

        <div class="welcome">

            <div class="welcome-icon">
                ✦
            </div>

            <h2>
                How can I help you?
            </h2>

            <p>
                Ask me anything or use one of the tools
                available in the chatbot.
            </p>

            <div class="suggestions">

                <button onclick="sendSuggestion(
                    'Plan a 3 day Goa trip from Mumbai'
                )">
                    🏖️ Goa Trip
                </button>

                <button onclick="sendSuggestion(
                    'Compare iPhone 16 Pro and Samsung Galaxy S25 Ultra'
                )">
                    📱 Compare Phones
                </button>

                <button onclick="sendSuggestion(
                    'Tell me about Porsche 911 GT3 RS'
                )">
                    🏎️ Car Details
                </button>

                <button onclick="sendSuggestion(
                    'Calculate 40 rupees times 500 with 5 percent GST'
                )">
                    🧮 Calculate
                </button>

            </div>

        </div>
    `;

    loadHistory();
}


// ============================================
// SUGGESTION
// ============================================

function sendSuggestion(text) {

    const input =
        document.getElementById("messageInput");

    input.value = text;

    sendMessage();
}


// ============================================
// ENTER KEY
// ============================================

function handleKey(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendMessage();
    }
}


// ============================================
// LOAD HISTORY
// ============================================

async function loadHistory() {

    try {

        const response =
            await fetch("/history");

        const data =
            await response.json();

        const history =
            document.getElementById("history");

        if (
            !data.success ||
            data.chats.length === 0
        ) {

            history.innerHTML =
                `<p class="empty-history">
                    No conversations yet
                </p>`;

            return;
        }


        history.innerHTML = "";


        data.chats.forEach(chat => {

            const item =
                document.createElement("div");

            item.className =
                "history-item";

            item.textContent =
                chat.title || "Conversation";

            item.title =
                chat.title || "Conversation";


            item.onclick = () =>
                loadConversation(
                    chat.session_id
                );


            history.appendChild(item);

        });

    } catch (error) {

        console.error(
            "History error:",
            error
        );

    }
}


// ============================================
// LOAD CONVERSATION
// ============================================

async function loadConversation(sessionId) {

    try {

        const response =
            await fetch(
                `/history/${sessionId}`
            );

        const data =
            await response.json();


        if (!data.success) {
            return;
        }


        const chat =
            document.getElementById("chat");

        chat.innerHTML = "";


        data.messages.forEach(message => {

            addMessage(
                message.role,
                message.content,
                message.tools || []
            );

        });

    } catch (error) {

        console.error(
            "Conversation error:",
            error
        );

    }
}


// ============================================
// TEST GEMINI
// ============================================

async function testGemini() {

    try {

        const response =
            await fetch(
                "/test-gemini",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();

        if (data.success) {

            alert(
                "✅ Gemini connection successful!"
            );

        } else {

            alert(
                "❌ Gemini connection failed:\n" +
                data.error
            );

        }

    } catch (error) {

        alert(
            "❌ Could not connect to Flask."
        );

    }
}


// ============================================
// LOAD TOOLS
// ============================================

async function loadTools() {

    const modal =
        document.getElementById("toolModal");

    const toolsList =
        document.getElementById("toolsList");


    modal.style.display = "flex";

    toolsList.innerHTML =
        "Loading tools...";


    try {

        const response =
            await fetch("/tools");

        const data =
            await response.json();


        if (
            !data.success ||
            !data.tools
        ) {

            toolsList.innerHTML =
                "Could not load tools.";

            return;
        }


        toolsList.innerHTML = "";


        data.tools.forEach(tool => {

            const div =
                document.createElement("div");

            div.className = "tool";

            div.innerHTML = `

                <strong>
                    ${tool.icon || "🔧"}
                    ${tool.name}
                </strong>

                <p>
                    ${tool.description || ""}
                </p>

            `;

            toolsList.appendChild(div);

        });

    } catch (error) {

        toolsList.innerHTML =
            "Error loading tools.";

    }
}


// ============================================
// CLOSE MODAL
// ============================================

function closeModal() {

    document.getElementById(
        "toolModal"
    ).style.display = "none";
}


// ============================================
// ESCAPE HTML
// ============================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;
}


// ============================================
// SCROLL
// ============================================

function scrollToBottom() {

    const container =
        document.querySelector(
            ".chat-container"
        );

    if (container) {

        container.scrollTop =
            container.scrollHeight;

    }
}


// ============================================
// INITIAL LOAD
// ============================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadHistory();

        const input =
            document.getElementById(
                "messageInput"
            );

        input.focus();

    }
);