/**
 * GoalMate Settings Component
 * Handles local user profile, AI Coach persona customization,
 * API key guide, data backup/restore, and safe data reset.
 */

const SettingsComponent = {
    render() {
        const store = window.store;
        if (!store) return;

        const container = document.getElementById('main-view-content');
        if (!container) return;

        const user = store.getUser();

        container.innerHTML = `
            <div class="view-page-wrapper settings-view">
                <div class="view-page-header">
                    <h2 class="view-page-title">⚙️ Settings & Local Profile</h2>
                    <p class="view-page-subtitle">Personalize your GoalMate experience, manage AI Coach preferences, and backup your local productivity data.</p>
                </div>

                <div class="settings-cards-grid">
                    <!-- Profile Card -->
                    <div class="card settings-card">
                        <div class="card-header">
                            <span class="card-title"><span class="icon">👤</span> Profile Details</span>
                        </div>
                        <form onsubmit="SettingsComponent.saveProfile(event)" class="settings-form">
                            <div class="form-group">
                                <label class="form-label">Your Name</label>
                                <input type="text" id="setting-name-input" class="form-input" 
                                    value="${user.name || 'Sanskriti'}" required 
                                    placeholder="Enter your name" />
                                <small class="form-help">This name dynamically updates the dashboard greeting and AI Coach interactions.</small>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Motto / Subtitle</label>
                                <input type="text" id="setting-title-input" class="form-input" 
                                    value="${user.title || 'Dream it. Plan it. Do it.'}" 
                                    placeholder="e.g. Dream it. Plan it. Do it." />
                            </div>

                            <div class="form-group">
                                <label class="form-label">AI Coach Persona Style</label>
                                <select id="setting-persona-input" class="form-input">
                                    <option value="High Energy (Hinata)" ${user.aiPersona === 'High Energy (Hinata)' ? 'selected' : ''}>High Energy & Relentless (Shoyo Hinata style)</option>
                                    <option value="Disciplined Strategist (Kageyama)" ${user.aiPersona === 'Disciplined Strategist (Kageyama)' ? 'selected' : ''}>Disciplined Strategist (Kageyama style)</option>
                                    <option value="Calm & Grounded (Daichi)" ${user.aiPersona === 'Calm & Grounded (Daichi)' ? 'selected' : ''}>Calm & Grounded Captain (Daichi style)</option>
                                </select>
                            </div>

                            <button type="submit" class="btn btn-primary">Save Profile Settings</button>
                        </form>
                    </div>

                    <!-- Gemini API Configuration Helper -->
                    <div class="card settings-card api-helper-card">
                        <div class="card-header">
                            <span class="card-title"><span class="icon">🤖</span> Google Gemini API Setup</span>
                        </div>
                        <div class="api-helper-content">
                            <p>GoalMate's AI Coach operates using <strong>Google Gemini</strong>.</p>
                            
                            <div class="api-guide-steps">
                                <div class="guide-step">
                                    <span class="step-num">1</span>
                                    <div class="step-text">
                                        <strong>Get a Free Gemini API Key:</strong>
                                        Visit <a href="https://aistudio.google.com/app/apikey" target="_blank" class="external-link">Google AI Studio ↗</a> to create a key.
                                    </div>
                                </div>
                                <div class="guide-step">
                                    <span class="step-num">2</span>
                                    <div class="step-text">
                                        <strong>Add to your <code>.env</code> file:</strong>
                                        <pre class="code-snippet-box">GEMINI_API_KEY=your_gemini_key_here</pre>
                                    </div>
                                </div>
                                <div class="guide-step">
                                    <span class="step-num">3</span>
                                    <div class="step-text">
                                        <strong>No Key? No Problem:</strong>
                                        The AI Coach includes an intelligent local fallback system that uses your real goals and tasks to give tailored advice even without an API key!
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Data Backup & Reset Card -->
                    <div class="card settings-card danger-zone-card">
                        <div class="card-header">
                            <span class="card-title"><span class="icon">💾</span> Data Management & Reset</span>
                        </div>
                        <div class="data-mgmt-content">
                            <p class="data-mgmt-desc">All your goals, tasks, and historical edits are stored in your browser's persistent LocalStorage.</p>

                            <div class="btn-group-wrap">
                                <button class="btn btn-outline" onclick="SettingsComponent.exportData()">
                                    📥 Export Data (JSON)
                                </button>
                                
                                <label class="btn btn-outline file-upload-btn">
                                    📤 Import Data (JSON)
                                    <input type="file" accept=".json" onchange="SettingsComponent.importData(event)" style="display:none;" />
                                </label>

                                <button class="btn btn-danger-outline" onclick="SettingsComponent.confirmReset()">
                                    ⚠️ Reset Demo Data
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    saveProfile(e) {
        e.preventDefault();
        const name = document.getElementById('setting-name-input').value.trim();
        const title = document.getElementById('setting-title-input').value.trim();
        const aiPersona = document.getElementById('setting-persona-input').value;

        window.store.updateUser({ name, title, aiPersona });
        alert("✅ Profile settings saved!");
        this.render();
        if (window.DashboardComponent) window.DashboardComponent.render();
    },

    exportData() {
        const jsonStr = window.store.exportJSON();
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `goalmate-backup-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    importData(e) {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            const success = window.store.importJSON(event.target.result);
            if (success) {
                alert("✅ Data imported successfully!");
                location.reload();
            } else {
                alert("❌ Invalid backup file.");
            }
        };
        reader.readAsText(file);
    },

    confirmReset() {
        if (confirm("Are you sure you want to reset all data back to the default demo state? This will overwrite your current progress records.")) {
            window.store.resetToDefaults();
            alert("🔄 Data has been reset to defaults.");
            location.reload();
        }
    }
};

window.SettingsComponent = SettingsComponent;
