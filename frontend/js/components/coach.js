/**
 * GoalMate AI Coach Right Panel Component
 * Context-aware coaching powered by Google Gemini API with smart fallback.
 */

const AICoach = {
    messages: [
        {
            role: "assistant",
            content: "Hey Sanskriti! 👋\nYou're doing great! Your consistency this week is amazing.\n\nKeep going — you're closer than you think."
        },
        {
            role: "user",
            content: "I'm feeling a bit unmotivated today. Can you give me a quick boost? 🥺"
        },
        {
            role: "assistant",
            content: "Of course! ✨\nRemember:\n*\"Progress isn't about being perfect, it's about showing up.\"*\n\nYou've already completed two tasks today and you're holding a strong streak! Let's focus on one small thing you can finish next."
        }
    ],
    isLoading: false,

    init() {
        this.render();
        this.checkAPIStatus();
    },

    async checkAPIStatus() {
        try {
            const res = await fetch('/api/coach/status');
            const data = await res.json();
            const badge = document.getElementById('coach-online-badge');
            if (badge) {
                if (data.gemini_configured) {
                    badge.innerHTML = '<span class="status-dot online"></span> Gemini Online';
                    badge.title = "Connected to live Google Gemini 2.5 Flash API";
                } else {
                    badge.innerHTML = '<span class="status-dot simulated"></span> Coach Active';
                    badge.title = "Operating in local coach mode (configure GEMINI_API_KEY in .env for live Gemini)";
                }
            }
        } catch (e) {
            console.log("Coach status check skipped:", e);
        }
    },

    render() {
        const container = document.getElementById('ai-coach-panel');
        if (!container) return;

        const user = window.store ? window.store.getUser() : { name: "Sanskriti" };

        container.innerHTML = `
            <div class="coach-container">
                <!-- Header -->
                <div class="coach-header">
                    <div class="coach-header-left">
                        <div class="coach-avatar-wrap">
                            <img src="/assets/images/hinata_avatar.jpg" alt="Coach Avatar" class="coach-header-avatar" />
                            <span class="avatar-ring-pulse"></span>
                        </div>
                        <div class="coach-title-wrap">
                            <h3 class="coach-title">AI Coach</h3>
                            <span id="coach-online-badge" class="coach-status"><span class="status-dot online"></span> Online</span>
                        </div>
                    </div>
                    <div class="coach-header-actions">
                        <button class="icon-btn-subtle" title="Clear Conversation" onclick="AICoach.clearChat()">🗑️</button>
                    </div>
                </div>

                <!-- Messages Feed -->
                <div id="coach-messages-feed" class="coach-messages-feed">
                    ${this.messages.map(m => this.renderMessageBubble(m)).join('')}
                    ${this.isLoading ? `
                        <div class="message-row assistant">
                            <img src="/assets/images/hinata_avatar.jpg" class="msg-avatar" />
                            <div class="msg-bubble assistant typing-indicator">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    ` : ''}
                </div>

                <!-- Suggestion Chips -->
                <div class="coach-suggestions-container">
                    <button class="suggestion-chip" onclick="AICoach.handleSuggestion('Plan my day')">⚡ Plan my day</button>
                    <button class="suggestion-chip" onclick="AICoach.handleSuggestion('Suggest study plan')">📚 Suggest study plan</button>
                    <button class="suggestion-chip" onclick="AICoach.handleSuggestion('Give me tips')">💡 Give me tips</button>
                    <button class="suggestion-chip" onclick="AICoach.handleSuggestion('Help me with my goals')">🎯 Help me with my goals</button>
                    <button class="suggestion-chip chip-gradio" onclick="window.AppRouter.navigate('studio')">🏐 AI Studio (Gradio)</button>
                </div>

                <!-- Input Row -->
                <div class="coach-input-area">
                    <form onsubmit="AICoach.handleSubmit(event)" class="coach-input-form">
                        <input 
                            type="text" 
                            id="coach-user-input" 
                            class="coach-input-field" 
                            placeholder="Type a message..." 
                            autocomplete="off"
                            ${this.isLoading ? 'disabled' : ''}
                        />
                        <button type="submit" class="coach-send-btn" ${this.isLoading ? 'disabled' : ''} title="Send message">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"></path>
                            </svg>
                        </button>
                    </form>
                </div>
            </div>
        `;

        this.scrollToBottom();
    },

    renderMessageBubble(msg) {
        const isAssistant = msg.role === 'assistant';
        const formattedText = this.formatMarkdown(msg.content);
        return `
            <div class="message-row ${isAssistant ? 'assistant' : 'user'}">
                ${isAssistant ? `<img src="/assets/images/hinata_avatar.jpg" class="msg-avatar" alt="Coach" />` : ''}
                <div class="msg-bubble ${isAssistant ? 'assistant' : 'user'}">
                    <div class="msg-text">${formattedText}</div>
                </div>
            </div>
        `;
    },

    formatMarkdown(text) {
        if (!text) return "";
        let escaped = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        
        // Bold
        escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Italics
        escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
        // Inline code
        escaped = escaped.replace(/`(.*?)`/g, '<code>$1</code>');
        // Bullet points
        escaped = escaped.replace(/^[\*\-]\s+(.*)$/gm, '<li class="chat-bullet">$1</li>');
        // Wrap lists if needed
        escaped = escaped.replace(/(<li.*<\/li>)/s, '<ul>$1</ul>');
        // Newlines
        escaped = escaped.replace(/\n/g, '<br/>');
        return escaped;
    },

    scrollToBottom() {
        setTimeout(() => {
            const feed = document.getElementById('coach-messages-feed');
            if (feed) feed.scrollTop = feed.scrollHeight;
        }, 50);
    },

    handleSuggestion(text) {
        const input = document.getElementById('coach-user-input');
        if (input) {
            input.value = text;
            this.sendMessage(text);
        }
    },

    handleSubmit(e) {
        e.preventDefault();
        const input = document.getElementById('coach-user-input');
        if (!input) return;
        const msg = input.value.trim();
        if (!msg || this.isLoading) return;
        input.value = '';
        this.sendMessage(msg);
    },

    async sendMessage(text) {
        // Add user message
        this.messages.push({ role: 'user', content: text });
        this.isLoading = true;
        this.render();

        // Build live context from store
        let contextPayload = {};
        let userName = "Sanskriti";

        if (window.store) {
            const user = window.store.getUser();
            userName = user.name || "Sanskriti";
            const goals = window.store.getGoals().map(g => ({
                id: g.id,
                title: g.title,
                category: g.category,
                progress: window.StreaksEngine ? window.StreaksEngine.calculateGoalProgress(g, window.store.state.history) : 50,
                milestones: g.milestones || []
            }));
            const tasks = window.store.getTodayTasks();
            const overview = window.StreaksEngine ? window.StreaksEngine.calculateOverviewStats(window.store) : {};

            contextPayload = {
                goals,
                tasks,
                streaks: {
                    currentStreak: overview.currentStreak || 5,
                    bestStreak: overview.bestStreak || 8,
                    weeklyProgress: overview.weeklyProgress || 72
                },
                recentActivity: window.store.getRecentActivity()
            };
        }

        try {
            const response = await fetch('/api/coach/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    userName,
                    context: contextPayload
                })
            });

            if (!response.ok) throw new Error("API returned status " + response.status);
            const data = await response.json();
            
            this.messages.push({
                role: 'assistant',
                content: data.reply || "Let's keep showing up every day! What's next on our agenda?"
            });
        } catch (err) {
            console.warn("Backend chat request failed, generating smart response:", err);
            // Local client-side fallback
            this.messages.push({
                role: 'assistant',
                content: `Hey ${userName}! 🌟 Keep your head up!\n\nRemember: *"Discipline is choosing what you want most over what you want now."*\n\nTake one of your active tasks and let's conquer it together! 🏐✨`
            });
        } finally {
            this.isLoading = false;
            this.render();
        }
    },

    clearChat() {
        const user = window.store ? window.store.getUser() : { name: "Sanskriti" };
        this.messages = [
            {
                role: "assistant",
                content: `Hey ${user.name}! 👋 Ready for a fresh start! How can I help you crush your goals today?`
            }
        ];
        this.render();
    }
};

window.AICoach = AICoach;
