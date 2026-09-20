/**
 * GoalMate Goals Page Component
 * Handles multiple goals display, filtering, creation modal with custom cover upload & milestone builders.
 */

const GoalsComponent = {
    filterCategory: 'All',
    editingGoalId: null,
    tempCoverDataUrl: null,
    tempMilestones: [],

    render() {
        const store = window.store;
        const streaks = window.StreaksEngine;
        if (!store || !streaks) return;

        const container = document.getElementById('main-view-content');
        if (!container) return;

        const allGoals = store.getGoals();
        const categories = ['All', ...new Set(allGoals.map(g => g.category))];

        const filteredGoals = this.filterCategory === 'All' 
            ? allGoals 
            : allGoals.filter(g => g.category === this.filterCategory);

        container.innerHTML = `
            <div class="view-page-wrapper">
                <div class="view-page-header flex-between">
                    <div>
                        <h2 class="view-page-title">🎯 Your Goals</h2>
                        <p class="view-page-subtitle">Track your ambitions, break them down into milestones, and build unwavering consistency.</p>
                    </div>
                    <button class="btn btn-primary" onclick="GoalsComponent.openAddModal()">
                        <span class="btn-icon">+</span> Add New Goal
                    </button>
                </div>

                <!-- Category Filters -->
                <div class="filter-pills-bar">
                    ${categories.map(cat => `
                        <button class="filter-pill ${this.filterCategory === cat ? 'active' : ''}" 
                            onclick="GoalsComponent.setCategoryFilter('${cat}')">
                            ${cat}
                        </button>
                    `).join('')}
                </div>

                <!-- Goals Grid -->
                ${filteredGoals.length === 0 ? `
                    <div class="empty-state-card">
                        <div class="empty-icon">🎯</div>
                        <h3>Ready to start?</h3>
                        <p>Create your first goal and turn an idea into something real.</p>
                        <button class="btn btn-primary" onclick="GoalsComponent.openAddModal()">+ Add Goal</button>
                    </div>
                ` : `
                    <div class="goals-cards-grid">
                        ${filteredGoals.map(goal => {
                            const progress = streaks.calculateGoalProgress(goal, store.state.history);
                            const daysLeft = streaks.getDaysRemaining(goal.targetDate);
                            const goalStreak = streaks.calculateStreak(goal.id, store.state.history);
                            const completedMilestones = (goal.milestones || []).filter(m => m.completed).length;
                            const totalMilestones = (goal.milestones || []).length;

                            return `
                                <div class="card goal-card-full" onclick="window.GoalDetailComponent.open('${goal.id}')">
                                    <div class="goal-card-cover-wrap">
                                        <img src="${goal.coverImage || '/assets/images/header_banner.png'}" 
                                            alt="${goal.title}" class="goal-card-cover-img" 
                                            onerror="this.src='/assets/images/header_banner.png'" />
                                        <span class="goal-card-cat-badge">${goal.category}</span>
                                        <div class="goal-card-actions-dropdown" onclick="event.stopPropagation()">
                                            <button class="icon-btn-circle" title="Edit Goal" onclick="GoalsComponent.openEditModal('${goal.id}')">✏️</button>
                                            <button class="icon-btn-circle danger" title="Delete Goal" onclick="GoalsComponent.confirmDeleteGoal('${goal.id}')">🗑️</button>
                                        </div>
                                    </div>

                                    <div class="goal-card-content">
                                        <h3 class="goal-card-title">${goal.title}</h3>
                                        <p class="goal-card-desc">${goal.description || 'No description provided.'}</p>

                                        <!-- Progress Bar -->
                                        <div class="goal-card-progress-section">
                                            <div class="flex-between progress-text-row">
                                                <span class="progress-label-small">Progress</span>
                                                <span class="progress-val-bold">${progress}%</span>
                                            </div>
                                            <div class="progress-bar-track">
                                                <div class="progress-bar-fill orange-gradient" style="width: ${progress}%;"></div>
                                            </div>
                                        </div>

                                        <!-- Milestones Summary -->
                                        <div class="goal-card-milestones-preview">
                                            <span class="milestones-count-text">📌 ${completedMilestones}/${totalMilestones} Milestones Completed</span>
                                            <div class="milestones-preview-list">
                                                ${(goal.milestones || []).slice(0, 3).map(m => `
                                                    <div class="milestone-preview-item ${m.completed ? 'done' : ''}">
                                                        <span class="m-check">${m.completed ? '✓' : '○'}</span>
                                                        <span class="m-name">${m.title}</span>
                                                    </div>
                                                `).join('')}
                                                ${totalMilestones > 3 ? `<span class="more-milestones">+${totalMilestones - 3} more</span>` : ''}
                                            </div>
                                        </div>

                                        <!-- Footer Meta -->
                                        <div class="goal-card-footer flex-between">
                                            <span class="meta-tag"><span class="icon">📅</span> ${daysLeft} days left</span>
                                            ${goalStreak.currentStreak > 0 ? `
                                                <span class="meta-tag streak-tag"><span class="icon">🔥</span> ${goalStreak.currentStreak}d streak</span>
                                            ` : `
                                                <span class="meta-tag frequency-tag">${goal.frequency || 'Daily'}</span>
                                            `}
                                        </div>
                                    </div>

                                    <div class="goal-card-bottom-bar">
                                        <span>Open Goal Details & Retroactive Tracker →</span>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `}
            </div>
        `;
    },

    setCategoryFilter(cat) {
        this.filterCategory = cat;
        this.render();
    },

    openAddModal() {
        this.editingGoalId = null;
        this.tempCoverDataUrl = '/assets/images/header_banner.png';
        this.tempMilestones = [
            { id: 'm-1', title: 'Complete prerequisite research', completed: true },
            { id: 'm-2', title: 'Finish fundamental projects', completed: false }
        ];
        this.showGoalModal("Add New Goal");
    },

    openEditModal(goalId) {
        const goal = window.store.getGoal(goalId);
        if (!goal) return;
        this.editingGoalId = goalId;
        this.tempCoverDataUrl = goal.coverImage || '/assets/images/header_banner.png';
        this.tempMilestones = JSON.parse(JSON.stringify(goal.milestones || []));
        this.showGoalModal("Edit Goal", goal);
    },

    showGoalModal(titleText, goalData = null) {
        const modalContainer = document.getElementById('global-modal-container');
        if (!modalContainer) return;

        const defaultTargetDate = goalData ? goalData.targetDate : new Date(Date.now() + 60*24*60*60*1000).toISOString().split('T')[0];

        modalContainer.innerHTML = `
            <div class="modal-backdrop" onclick="GoalsComponent.closeModal()">
                <div class="modal-card modal-lg" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3 class="modal-title">${titleText}</h3>
                        <button class="modal-close-btn" onclick="GoalsComponent.closeModal()">✕</button>
                    </div>

                    <form onsubmit="GoalsComponent.saveGoal(event)" class="modal-form">
                        <div class="form-row-2">
                            <div class="form-group">
                                <label class="form-label">Goal Title *</label>
                                <input type="text" id="goal-title-input" class="form-input" required 
                                    placeholder="e.g. Become Internship Ready" 
                                    value="${goalData ? goalData.title : ''}" />
                            </div>

                            <div class="form-group">
                                <label class="form-label">Category</label>
                                <select id="goal-cat-input" class="form-input">
                                    <option value="Web Dev" ${goalData && goalData.category === 'Web Dev' ? 'selected' : ''}>Web Dev</option>
                                    <option value="DSA" ${goalData && goalData.category === 'DSA' ? 'selected' : ''}>DSA / Coding</option>
                                    <option value="Career" ${goalData && goalData.category === 'Career' ? 'selected' : ''}>Career</option>
                                    <option value="Fitness" ${goalData && goalData.category === 'Fitness' ? 'selected' : ''}>Fitness</option>
                                    <option value="Personal" ${goalData && goalData.category === 'Personal' ? 'selected' : ''}>Personal Growth</option>
                                    <option value="Academics" ${goalData && goalData.category === 'Academics' ? 'selected' : ''}>Academics</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Description</label>
                            <textarea id="goal-desc-input" class="form-textarea" rows="2" 
                                placeholder="Describe why this goal matters and what success looks like...">${goalData ? goalData.description : ''}</textarea>
                        </div>

                        <div class="form-row-2">
                            <div class="form-group">
                                <label class="form-label">Target Date</label>
                                <input type="date" id="goal-date-input" class="form-input" value="${defaultTargetDate}" />
                            </div>

                            <div class="form-group">
                                <label class="form-label">Tracking Frequency</label>
                                <select id="goal-freq-input" class="form-input">
                                    <option value="daily" ${goalData && goalData.frequency === 'daily' ? 'selected' : ''}>Daily</option>
                                    <option value="weekly" ${goalData && goalData.frequency === 'weekly' ? 'selected' : ''}>Weekly</option>
                                    <option value="custom" ${goalData && goalData.frequency === 'custom' ? 'selected' : ''}>Custom</option>
                                </select>
                            </div>
                        </div>

                        <!-- Custom Goal Cover Image Upload & Presets -->
                        <div class="form-group cover-upload-group">
                            <label class="form-label">Goal Cover Image</label>
                            <div class="cover-preview-wrapper">
                                <div class="cover-preview-box">
                                    <img id="cover-preview-img" src="${this.tempCoverDataUrl}" alt="Cover Preview" />
                                </div>
                                <div class="cover-upload-controls">
                                    <label class="btn btn-sm btn-outline file-upload-btn">
                                        📁 Upload Custom Image
                                        <input type="file" accept="image/*" onchange="GoalsComponent.handleImageUpload(event)" style="display:none;" />
                                    </label>
                                    <button type="button" class="btn btn-sm btn-ghost" onclick="GoalsComponent.removeCover()">Remove Cover</button>
                                    
                                    <div class="cover-preset-picker">
                                        <span class="preset-label">Or choose preset:</span>
                                        <div class="preset-thumbnails">
                                            <img src="/assets/images/header_banner.png" class="preset-thumb" title="Sunset Court" onclick="GoalsComponent.selectPreset('/assets/images/header_banner.png')" />
                                            <img src="/assets/images/sidebar_hinata.png" class="preset-thumb" title="Hinata Sunset" onclick="GoalsComponent.selectPreset('/assets/images/sidebar_hinata.png')" />
                                            <img src="/assets/images/hinata_avatar.jpg" class="preset-thumb" title="Hinata Focus" onclick="GoalsComponent.selectPreset('/assets/images/hinata_avatar.jpg')" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Milestones Builder -->
                        <div class="form-group milestones-builder-group">
                            <div class="flex-between">
                                <label class="form-label">Milestones (${this.tempMilestones.length})</label>
                                <button type="button" class="btn btn-xs btn-outline" onclick="GoalsComponent.addTempMilestone()">+ Add Milestone</button>
                            </div>
                            <div id="modal-milestones-list" class="modal-milestones-list">
                                ${this.tempMilestones.map((m, idx) => `
                                    <div class="milestone-input-row">
                                        <input type="checkbox" ${m.completed ? 'checked' : ''} 
                                            onchange="GoalsComponent.toggleTempMilestone(${idx})" />
                                        <input type="text" class="form-input form-input-sm" 
                                            value="${m.title}" 
                                            oninput="GoalsComponent.updateTempMilestoneTitle(${idx}, this.value)" 
                                            placeholder="Milestone title..." />
                                        <button type="button" class="icon-btn-subtle danger" onclick="GoalsComponent.removeTempMilestone(${idx})">✕</button>
                                    </div>
                                `).join('')}
                            </div>
                        </div>

                        <div class="modal-actions">
                            <button type="button" class="btn btn-outline" onclick="GoalsComponent.closeModal()">Cancel</button>
                            <button type="submit" class="btn btn-primary">${goalData ? 'Save Changes' : 'Create Goal'}</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    handleImageUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            this.tempCoverDataUrl = event.target.result;
            const previewEl = document.getElementById('cover-preview-img');
            if (previewEl) previewEl.src = this.tempCoverDataUrl;
        };
        reader.readAsDataURL(file);
    },

    selectPreset(url) {
        this.tempCoverDataUrl = url;
        const previewEl = document.getElementById('cover-preview-img');
        if (previewEl) previewEl.src = url;
    },

    removeCover() {
        this.tempCoverDataUrl = '/assets/images/header_banner.png';
        const previewEl = document.getElementById('cover-preview-img');
        if (previewEl) previewEl.src = this.tempCoverDataUrl;
    },

    addTempMilestone() {
        this.tempMilestones.push({
            id: 'm-' + Date.now(),
            title: '',
            completed: false
        });
        this.renderMilestonesList();
    },

    removeTempMilestone(idx) {
        this.tempMilestones.splice(idx, 1);
        this.renderMilestonesList();
    },

    toggleTempMilestone(idx) {
        if (this.tempMilestones[idx]) {
            this.tempMilestones[idx].completed = !this.tempMilestones[idx].completed;
        }
    },

    updateTempMilestoneTitle(idx, val) {
        if (this.tempMilestones[idx]) {
            this.tempMilestones[idx].title = val;
        }
    },

    renderMilestonesList() {
        const container = document.getElementById('modal-milestones-list');
        if (!container) return;
        container.innerHTML = this.tempMilestones.map((m, idx) => `
            <div class="milestone-input-row">
                <input type="checkbox" ${m.completed ? 'checked' : ''} 
                    onchange="GoalsComponent.toggleTempMilestone(${idx})" />
                <input type="text" class="form-input form-input-sm" 
                    value="${m.title}" 
                    oninput="GoalsComponent.updateTempMilestoneTitle(${idx}, this.value)" 
                    placeholder="Milestone title..." />
                <button type="button" class="icon-btn-subtle danger" onclick="GoalsComponent.removeTempMilestone(${idx})">✕</button>
            </div>
        `).join('');
    },

    saveGoal(e) {
        e.preventDefault();
        const title = document.getElementById('goal-title-input').value.trim();
        const category = document.getElementById('goal-cat-input').value;
        const description = document.getElementById('goal-desc-input').value.trim();
        const targetDate = document.getElementById('goal-date-input').value;
        const frequency = document.getElementById('goal-freq-input').value;

        if (!title) return;

        // Filter out empty milestones
        const validMilestones = this.tempMilestones.filter(m => m.title.trim().length > 0);

        const goalPayload = {
            title,
            category,
            description,
            targetDate,
            frequency,
            coverImage: this.tempCoverDataUrl || '/assets/images/header_banner.png',
            milestones: validMilestones
        };

        if (this.editingGoalId) {
            window.store.updateGoal(this.editingGoalId, goalPayload);
        } else {
            window.store.addGoal(goalPayload);
        }

        this.closeModal();
        this.render();
        if (window.DashboardComponent) window.DashboardComponent.render();
    },

    confirmDeleteGoal(id) {
        const goal = window.store.getGoal(id);
        if (!goal) return;
        if (confirm(`Are you sure you want to delete the goal "${goal.title}"? This cannot be undone.`)) {
            window.store.deleteGoal(id);
            this.render();
            if (window.DashboardComponent) window.DashboardComponent.render();
        }
    },

    closeModal() {
        const modalContainer = document.getElementById('global-modal-container');
        if (modalContainer) modalContainer.innerHTML = '';
    }
};

window.GoalsComponent = GoalsComponent;
