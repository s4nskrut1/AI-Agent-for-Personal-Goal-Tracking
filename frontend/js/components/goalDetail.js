/**
 * GoalMate Goal Detail Component
 * Displays comprehensive goal metrics, milestone management, linked tasks,
 * and the RETROACTIVE PROGRESS CALENDAR (allows editing any previous date).
 */

const GoalDetailComponent = {
    currentGoalId: null,

    open(goalId) {
        this.currentGoalId = goalId;
        window.AppRouter.navigate('goal-detail');
    },

    render() {
        const store = window.store;
        const streaks = window.StreaksEngine;
        if (!store || !streaks || !this.currentGoalId) return;

        const goal = store.getGoal(this.currentGoalId);
        if (!goal) {
            window.AppRouter.navigate('goals');
            return;
        }

        const container = document.getElementById('main-view-content');
        if (!container) return;

        const progress = streaks.calculateGoalProgress(goal, store.state.history);
        const daysLeft = streaks.getDaysRemaining(goal.targetDate);
        const streakInfo = streaks.calculateStreak(goal.id, store.state.history);
        const history = store.getGoalHistory(goal.id);
        const milestones = goal.milestones || [];
        const completedMilestones = milestones.filter(m => m.completed).length;

        // Related tasks
        const linkedTasks = store.getTasks().filter(t => t.goalId === goal.id);

        // Get past 21 days for the retroactive calendar matrix
        const datesList = streaks.getPastDatesList(21);

        container.innerHTML = `
            <div class="view-page-wrapper goal-detail-view">
                <!-- Back Navigation Bar -->
                <div class="detail-nav-bar flex-between">
                    <button class="btn btn-sm btn-outline back-btn" onclick="window.AppRouter.navigate('goals')">
                        ← Back to Goals
                    </button>
                    <div class="detail-actions-group">
                        <button class="btn btn-sm btn-outline" onclick="window.GoalsComponent.openEditModal('${goal.id}')">✏️ Edit Goal</button>
                        <button class="btn btn-sm btn-danger-outline" onclick="GoalDetailComponent.deleteThisGoal()">🗑️ Delete</button>
                    </div>
                </div>

                <!-- Goal Hero Header with Cover Image -->
                <div class="goal-hero-card" style="background-image: linear-gradient(rgba(15, 23, 42, 0.7), rgba(15, 23, 42, 0.85)), url('${goal.coverImage || '/assets/images/header_banner.png'}');">
                    <div class="goal-hero-content">
                        <div class="goal-hero-top-row">
                            <span class="category-pill-lg">${goal.category}</span>
                            <span class="frequency-badge">Tracking: ${goal.frequency.toUpperCase()}</span>
                            <span class="status-chip-on-track">🟢 On Track</span>
                        </div>
                        <h1 class="goal-hero-title">${goal.title}</h1>
                        <p class="goal-hero-desc">${goal.description || 'Focus, consistency, and daily execution.'}</p>
                        
                        <div class="goal-hero-metrics">
                            <div class="hero-metric-item">
                                <span class="metric-num">${progress}%</span>
                                <span class="metric-label">Complete</span>
                            </div>
                            <div class="hero-metric-divider"></div>
                            <div class="hero-metric-item">
                                <span class="metric-num">🔥 ${streakInfo.currentStreak} Days</span>
                                <span class="metric-label">Current Streak</span>
                            </div>
                            <div class="hero-metric-divider"></div>
                            <div class="hero-metric-item">
                                <span class="metric-num">⚡ ${streakInfo.bestStreak} Days</span>
                                <span class="metric-label">Best Streak</span>
                            </div>
                            <div class="hero-metric-divider"></div>
                            <div class="hero-metric-item">
                                <span class="metric-num">📅 ${daysLeft}</span>
                                <span class="metric-label">Days Left</span>
                            </div>
                        </div>

                        <!-- Big Progress Bar -->
                        <div class="progress-bar-track hero-track">
                            <div class="progress-bar-fill orange-gradient" style="width: ${progress}%;"></div>
                        </div>
                    </div>
                </div>

                <!-- RETROACTIVE PROGRESS TRACKING MATRIX (CORE FEATURE) -->
                <div class="card retroactive-tracker-card">
                    <div class="card-header flex-between">
                        <div>
                            <span class="card-title"><span class="icon">📅</span> Retroactive Activity & History Calendar</span>
                            <p class="card-subtitle-sub">Forgot to log yesterday or last week? Click ANY date below to mark it completed or incomplete and immediately recalculate your streak!</p>
                        </div>
                        <div class="calendar-legend">
                            <span class="leg-item"><span class="leg-box done">✓</span> Completed</span>
                            <span class="leg-item"><span class="leg-box missed">○</span> Incomplete</span>
                            <span class="leg-item"><span class="leg-box rest">—</span> Rest / Skip</span>
                        </div>
                    </div>

                    <!-- Interactive Dates Grid -->
                    <div class="retroactive-dates-grid">
                        ${datesList.map(item => {
                            const entry = history[item.dateStr];
                            const status = entry ? entry.status : 'untracked';
                            const note = entry && entry.note ? entry.note : '';

                            let symbol = '—';
                            let statusClass = 'untracked';
                            if (status === 'completed') {
                                symbol = '✓';
                                statusClass = 'done';
                            } else if (status === 'incomplete') {
                                symbol = '○';
                                statusClass = 'missed';
                            } else if (status === 'rest') {
                                symbol = '—';
                                statusClass = 'rest';
                            }

                            return `
                                <div class="date-tile ${statusClass} ${item.isToday ? 'tile-today' : ''}" 
                                    onclick="GoalDetailComponent.openDateEditorModal('${item.dateStr}')"
                                    title="${item.dateStr}: ${status.toUpperCase()} ${note ? '— ' + note : ''} (Click to edit)">
                                    <span class="tile-weekday">${item.dayName}</span>
                                    <span class="tile-daynum">${item.dayNum}</span>
                                    <span class="tile-symbol">${symbol}</span>
                                    ${item.isToday ? `<span class="tile-today-badge">Today</span>` : ''}
                                    ${note ? `<span class="tile-has-note-dot" title="${note}"></span>` : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>

                    <div class="retroactive-callout">
                        💡 <strong>Real-time Streak Engine:</strong> Selecting past dates dynamically computes consecutive daily completions backwards from today. Try clicking a previous incomplete date and switching it to Completed to see your streak rise!
                    </div>
                </div>

                <!-- Two-Column Section: Milestones + Linked Tasks -->
                <div class="detail-two-col-grid">
                    <!-- Column 1: Milestones Checklist -->
                    <div class="card detail-milestones-card">
                        <div class="card-header flex-between">
                            <span class="card-title"><span class="icon">📌</span> Milestones (${completedMilestones}/${milestones.length})</span>
                            <button class="btn btn-xs btn-outline" onclick="GoalDetailComponent.promptAddMilestone()">+ Add Milestone</button>
                        </div>

                        <div class="milestones-checklist-interactive">
                            ${milestones.length === 0 ? `
                                <p class="text-muted-p">No milestones added yet. Add milestones to track step-by-step progress!</p>
                            ` : milestones.map(m => `
                                <div class="milestone-check-row ${m.completed ? 'm-done' : ''}" 
                                    onclick="GoalDetailComponent.toggleMilestone('${m.id}')">
                                    <div class="m-checkbox ${m.completed ? 'checked' : ''}">
                                        ${m.completed ? '✓' : ''}
                                    </div>
                                    <span class="m-title-text">${m.title}</span>
                                    <button class="icon-btn-subtle danger" title="Delete milestone" 
                                        onclick="event.stopPropagation(); GoalDetailComponent.deleteMilestone('${m.id}')">✕</button>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Column 2: Linked Tasks -->
                    <div class="card detail-tasks-card">
                        <div class="card-header flex-between">
                            <span class="card-title"><span class="icon">📋</span> Goal Tasks</span>
                            <button class="btn btn-xs btn-outline" onclick="GoalDetailComponent.promptAddTask()">+ Add Task</button>
                        </div>

                        <div class="linked-tasks-list">
                            ${linkedTasks.length === 0 ? `
                                <p class="text-muted-p">No specific tasks created for this goal yet. Add daily focus tasks to build momentum!</p>
                            ` : linkedTasks.map(t => `
                                <div class="task-row ${t.completed ? 'task-done' : ''}" 
                                    onclick="GoalDetailComponent.toggleTask('${t.id}')">
                                    <div class="task-checkbox-custom ${t.completed ? 'checked' : ''}">
                                        ${t.completed ? '✓' : ''}
                                    </div>
                                    <div class="task-title-wrap">
                                        <span class="task-title-text">${t.title}</span>
                                    </div>
                                    <div class="task-meta-pills">
                                        <span class="duration-pill">${t.duration}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Modal to Edit ANY Past Date's Progress
    openDateEditorModal(dateStr) {
        const store = window.store;
        const goal = store.getGoal(this.currentGoalId);
        if (!goal) return;

        const history = store.getGoalHistory(goal.id);
        const existingEntry = history[dateStr] || { status: 'untracked', note: '' };

        const modalContainer = document.getElementById('global-modal-container');
        if (!modalContainer) return;

        // Friendly date formatting
        const dateObj = new Date(dateStr + 'T00:00:00');
        const formattedDateTitle = dateObj.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        modalContainer.innerHTML = `
            <div class="modal-backdrop" onclick="GoalDetailComponent.closeModal()">
                <div class="modal-card" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <div>
                            <span class="modal-supertitle">EDIT HISTORICAL PROGRESS</span>
                            <h3 class="modal-title">${formattedDateTitle}</h3>
                        </div>
                        <button class="modal-close-btn" onclick="GoalDetailComponent.closeModal()">✕</button>
                    </div>

                    <form onsubmit="GoalDetailComponent.saveDateProgress(event, '${dateStr}')" class="modal-form">
                        <div class="form-group">
                            <label class="form-label">Completion Status for this Day</label>
                            <div class="radio-status-selector">
                                <label class="radio-card ${existingEntry.status === 'completed' ? 'selected' : ''}">
                                    <input type="radio" name="dateStatus" value="completed" ${existingEntry.status === 'completed' ? 'checked' : ''} />
                                    <div class="radio-card-content">
                                        <span class="radio-icon">✓</span>
                                        <strong>Completed</strong>
                                        <small>Target activity was achieved</small>
                                    </div>
                                </label>

                                <label class="radio-card ${existingEntry.status === 'incomplete' ? 'selected' : ''}">
                                    <input type="radio" name="dateStatus" value="incomplete" ${existingEntry.status === 'incomplete' ? 'checked' : ''} />
                                    <div class="radio-card-content">
                                        <span class="radio-icon">○</span>
                                        <strong>Not Completed</strong>
                                        <small>Did not fulfill target on this date</small>
                                    </div>
                                </label>

                                <label class="radio-card ${existingEntry.status === 'rest' ? 'selected' : ''}">
                                    <input type="radio" name="dateStatus" value="rest" ${existingEntry.status === 'rest' ? 'checked' : ''} />
                                    <div class="radio-card-content">
                                        <span class="radio-icon">—</span>
                                        <strong>Rest / Scheduled Off</strong>
                                        <small>Planned rest day (doesn't break streak)</small>
                                    </div>
                                </label>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Activity Journal Note (Optional)</label>
                            <textarea id="history-note-input" class="form-textarea" rows="2" 
                                placeholder="e.g. Practiced 45m DSA recursion, solved 2 medium problems">${existingEntry.note || ''}</textarea>
                        </div>

                        <div class="modal-actions">
                            <button type="button" class="btn btn-outline" onclick="GoalDetailComponent.closeModal()">Cancel</button>
                            <button type="submit" class="btn btn-primary">Save Changes & Recalculate</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    saveDateProgress(e, dateStr) {
        e.preventDefault();
        const selectedRadio = document.querySelector('input[name="dateStatus"]:checked');
        const status = selectedRadio ? selectedRadio.value : 'completed';
        const note = document.getElementById('history-note-input').value;

        window.store.setGoalDateStatus(this.currentGoalId, dateStr, status, note);
        
        // Play audio feedback
        if (window.FocusTimer) window.FocusTimer.playChime();

        this.closeModal();
        this.render();
        if (window.DashboardComponent) window.DashboardComponent.render();
    },

    toggleMilestone(milestoneId) {
        window.store.toggleMilestone(this.currentGoalId, milestoneId);
        if (window.FocusTimer) window.FocusTimer.playChime();
        this.render();
        if (window.DashboardComponent) window.DashboardComponent.render();
    },

    promptAddMilestone() {
        const title = prompt("Enter new milestone title:");
        if (title && title.trim()) {
            window.store.addMilestone(this.currentGoalId, title.trim());
            this.render();
            if (window.DashboardComponent) window.DashboardComponent.render();
        }
    },

    deleteMilestone(milestoneId) {
        if (confirm("Delete this milestone?")) {
            window.store.deleteMilestone(this.currentGoalId, milestoneId);
            this.render();
            if (window.DashboardComponent) window.DashboardComponent.render();
        }
    },

    toggleTask(taskId) {
        window.store.toggleTask(taskId);
        if (window.FocusTimer) window.FocusTimer.playChime();
        this.render();
        if (window.DashboardComponent) window.DashboardComponent.render();
    },

    promptAddTask() {
        const title = prompt("Enter task title for this goal:");
        if (title && title.trim()) {
            const goal = window.store.getGoal(this.currentGoalId);
            window.store.addTask({
                goalId: this.currentGoalId,
                title: title.trim(),
                category: goal ? goal.category : 'General',
                duration: '30 min',
                isToday: true
            });
            this.render();
            if (window.DashboardComponent) window.DashboardComponent.render();
        }
    },

    deleteThisGoal() {
        const goal = window.store.getGoal(this.currentGoalId);
        if (!goal) return;
        if (confirm(`Are you sure you want to delete "${goal.title}"?`)) {
            window.store.deleteGoal(this.currentGoalId);
            window.AppRouter.navigate('goals');
        }
    },

    closeModal() {
        const modalContainer = document.getElementById('global-modal-container');
        if (modalContainer) modalContainer.innerHTML = '';
    }
};

window.GoalDetailComponent = GoalDetailComponent;
