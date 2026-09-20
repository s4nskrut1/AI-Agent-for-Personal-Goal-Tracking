/**
 * GoalMate Dashboard Component (Clean Slate & User-Driven)
 * Timer removed, clean empty states, darker cinematic header banner.
 */

const DashboardComponent = {
    render() {
        const store = window.store;
        const streaks = window.StreaksEngine;
        if (!store || !streaks) return;

        const container = document.getElementById('main-view-content');
        if (!container) return;

        const user = store.getUser();
        const userNameMarkup = user.name
            ? `<br/><span class="user-display-name">${user.name}</span>`
            : '';
        const goals = store.getGoals();
        const todayTasks = store.getTodayTasks();
        const stats = streaks.calculateOverviewStats(store);
        const weeklyData = streaks.getWeeklyChartData(store);
        const recentActivity = store.getRecentActivity();

        // Get greeting by time of day
        const hour = new Date().getHours();
        let greetingWord = "Good Evening";
        if (hour < 12) greetingWord = "Good Morning";
        else if (hour < 17) greetingWord = "Good Afternoon";

        const primaryGoal = goals.length > 0 ? goals[0] : null;
        let primaryGoalProgress = 0;
        let daysLeft = 0;
        let completedMilestonesCount = 0;

        if (primaryGoal) {
            primaryGoalProgress = streaks.calculateGoalProgress(primaryGoal, store.state.history);
            daysLeft = streaks.getDaysRemaining(primaryGoal.targetDate);
            completedMilestonesCount = (primaryGoal.milestones || []).filter(m => m.completed).length;
        }

        container.innerHTML = `
            <div class="dashboard-wrapper">
                <!-- Hero Header Banner with Darker Cinematic Sunset Art -->
                <div class="dashboard-hero-banner" style="background-image: url('/assets/images/header_banner.png');">
                    <div class="banner-cinematic-overlay"></div>
                    <div class="banner-content">
                        <div class="banner-left">
                            <div class="greeting-badge">
                                <span class="greeting-sun-icon">☀️</span>
                                <span class="greeting-title">${greetingWord}${userNameMarkup}</span>
                            </div>
                            <p class="greeting-subtitle">${user.title || "Dream it. Plan it. Do it."}</p>
                        </div>
                    </div>
                </div>

                <!-- 4 Top Statistics Cards (Live Dynamically Calculated) -->
                <div class="stats-grid">
                    <div class="card stat-card stat-orange" onclick="window.AppRouter.navigate('goals')">
                        <div class="stat-icon-wrap bg-orange-light">
                            <span class="stat-emoji">🎯</span>
                        </div>
                        <div class="stat-info">
                            <span class="stat-value">${stats.activeGoals}</span>
                            <span class="stat-label">Active Goals</span>
                        </div>
                    </div>

                    <div class="card stat-card stat-blue">
                        <div class="stat-icon-wrap bg-blue-light">
                            <span class="stat-emoji">☑️</span>
                        </div>
                        <div class="stat-info">
                            <span class="stat-value">${stats.tasksTodayTotal > 0 ? `${stats.tasksTodayCompleted}/${stats.tasksTodayTotal}` : '0'}</span>
                            <span class="stat-label">Tasks Today</span>
                        </div>
                    </div>

                    <div class="card stat-card stat-flame">
                        <div class="stat-icon-wrap bg-flame-light">
                            <span class="stat-emoji">🔥</span>
                        </div>
                        <div class="stat-info">
                            <span class="stat-value">${stats.currentStreak} days</span>
                            <span class="stat-label">Current Streak</span>
                        </div>
                    </div>

                    <div class="card stat-card stat-green">
                        <div class="stat-icon-wrap bg-green-light">
                            <span class="stat-emoji">📈</span>
                        </div>
                        <div class="stat-info">
                            <span class="stat-value">${stats.weeklyProgress}%</span>
                            <span class="stat-label">Weekly Progress</span>
                        </div>
                    </div>
                </div>

                <!-- Main Content Grid -->
                <div class="dashboard-main-grid">
                    <!-- Column 1: Current Goal / Empty Goal Card + Weekly Progress -->
                    <div class="dashboard-col col-left">
                        ${primaryGoal ? `
                            <!-- Current Goal Card -->
                            <div class="card current-goal-card" onclick="window.GoalDetailComponent.open('${primaryGoal.id}')">
                                <div class="current-goal-header">
                                    <span class="current-goal-badge"><span class="badge-icon">🎯</span> Primary Goal</span>
                                    <button class="edit-goal-quick-btn" title="View details" onclick="event.stopPropagation(); window.GoalDetailComponent.open('${primaryGoal.id}')">✏️</button>
                                </div>
                                
                                <div class="current-goal-body">
                                    <div class="goal-cover-thumb-wrap">
                                        <img src="${primaryGoal.coverImage || '/assets/images/header_banner.png'}" alt="Goal Cover" class="goal-cover-thumb" onerror="this.src='/assets/images/header_banner.png'" />
                                    </div>
                                    <div class="goal-details-info">
                                        <h3 class="goal-main-title">${primaryGoal.title}</h3>
                                        <p class="goal-main-desc">${primaryGoal.description || 'No description provided.'}</p>
                                        
                                        <div class="progress-bar-container">
                                            <div class="progress-bar-track">
                                                <div class="progress-bar-fill orange-gradient" style="width: ${primaryGoalProgress}%;"></div>
                                            </div>
                                            <span class="progress-percentage-label">${primaryGoalProgress}%</span>
                                        </div>

                                        <div class="goal-meta-chips">
                                            <span class="meta-chip"><span class="chip-icon">👤</span> ${completedMilestonesCount}/${(primaryGoal.milestones || []).length} Milestones</span>
                                            <span class="meta-chip"><span class="chip-icon">📅</span> ${daysLeft} days Left</span>
                                            <span class="meta-chip status-chip-on-track"><span class="chip-icon">🟢</span> On Track</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ` : `
                            <!-- Empty Goals Prompt -->
                            <div class="card empty-state-dash-card" onclick="window.GoalsComponent.openAddModal()">
                                <div class="empty-dash-icon">🎯</div>
                                <h3 class="empty-dash-title">Ready to start?</h3>
                                <p class="empty-dash-desc">Create your first goal and turn an idea into something real.</p>
                                <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); window.GoalsComponent.openAddModal()">
                                    + Add Goal
                                </button>
                            </div>
                        `}

                        <!-- Weekly Progress Stacked Chart -->
                        <div class="card weekly-progress-card">
                            <div class="card-header flex-between">
                                <span class="card-title"><span class="icon">📊</span> Weekly Progress</span>
                                <div class="chart-header-actions">
                                    <span class="chart-time-pill">This Week ▾</span>
                                </div>
                            </div>

                            <div class="chart-canvas-wrapper">
                                <div class="stacked-bar-chart">
                                    ${weeklyData.map(d => `
                                        <div class="bar-column ${d.isToday ? 'current-day-bar' : ''}">
                                            <div class="bar-segments-stack ${d.totalHeightPercent ? '' : 'is-empty'}" style="height: ${d.totalHeightPercent}%;">
                                                <div class="bar-seg seg-study" style="flex: ${d.study};" title="DSA / Study"></div>
                                                <div class="bar-seg seg-project" style="flex: ${d.projects};" title="Web Dev / Projects"></div>
                                                <div class="bar-seg seg-personal" style="flex: ${d.personal};" title="Personal"></div>
                                                <div class="bar-seg seg-other" style="flex: ${d.others};" title="Fitness / Other"></div>
                                            </div>
                                            <span class="bar-day-label ${d.isToday ? 'active-day-label' : ''}">${d.day}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>

                            <!-- Legend -->
                            <div class="chart-legend">
                                <span class="legend-item"><span class="legend-dot seg-study"></span> Study</span>
                                <span class="legend-item"><span class="legend-dot seg-project"></span> Projects</span>
                                <span class="legend-item"><span class="legend-dot seg-personal"></span> Personal</span>
                                <span class="legend-item"><span class="legend-dot seg-other"></span> Others</span>
                            </div>
                        </div>

                        <!-- Recent Activity -->
                        <div class="card recent-activity-card">
                            <div class="card-header flex-between">
                                <span class="card-title"><span class="icon">🕒</span> Recent Activity</span>
                            </div>
                            <div class="activity-timeline-list">
                                ${recentActivity.length === 0 ? `
                                    <p class="text-muted-p" style="padding: 10px 0; font-size: 0.84rem;">Your progress and task activity will appear here as you start working.</p>
                                ` : recentActivity.slice(0, 5).map(act => `
                                    <div class="activity-item">
                                        <div class="act-icon-dot ${act.type}">
                                            ${act.type === 'task' ? '✓' : act.type === 'streak' ? '🔥' : '🎯'}
                                        </div>
                                        <div class="act-text-wrap">
                                            <span class="act-text">${act.text}</span>
                                            <span class="act-time">${act.timeAgo}</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>

                    <!-- Column 2: Today's Tasks + Your Goals -->
                    <div class="dashboard-col col-right">
                        <!-- Today's Tasks Card -->
                        <div class="card tasks-card">
                            <div class="card-header flex-between">
                                <span class="card-title"><span class="icon">☑️</span> Today's Tasks</span>
                                <button class="btn btn-xs btn-outline" onclick="DashboardComponent.promptQuickAddTask()">+ Add Task</button>
                            </div>

                            <div class="tasks-checklist">
                                ${todayTasks.length === 0 ? `
                                    <div class="empty-tasks-box">
                                        <p class="empty-tasks-text">No tasks scheduled yet for today.</p>
                                        <button class="btn btn-sm btn-outline" onclick="DashboardComponent.promptQuickAddTask()">+ Create First Task</button>
                                    </div>
                                ` : todayTasks.map(t => `
                                    <div class="task-row ${t.completed ? 'task-done' : ''}" onclick="DashboardComponent.toggleTask('${t.id}')">
                                        <div class="task-checkbox-custom ${t.completed ? 'checked' : ''}">
                                            ${t.completed ? '✓' : ''}
                                        </div>
                                        <div class="task-title-wrap">
                                            <span class="task-title-text">${t.title}</span>
                                        </div>
                                        <div class="task-meta-pills">
                                            <span class="category-pill pill-${t.category.toLowerCase().replace(/[^a-z]/g, '')}">${t.category}</span>
                                            <span class="duration-pill">${t.duration}</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>

                            <div class="card-footer-action">
                                <button class="add-task-quick-btn" onclick="DashboardComponent.promptQuickAddTask()">
                                    <span class="plus-icon">+</span> Add new task
                                </button>
                            </div>
                        </div>

                        <!-- Your Goals List -->
                        <div class="card your-goals-summary-card">
                            <div class="card-header flex-between">
                                <span class="card-title"><span class="icon">🎯</span> Your Goals</span>
                                <button class="link-btn" onclick="window.AppRouter.navigate('goals')">View all →</button>
                            </div>

                            <div class="goals-mini-list">
                                ${goals.length === 0 ? `
                                    <p class="text-muted-p" style="font-size: 0.84rem; padding: 8px 0;">No goals added yet. Click "+ Add New Goal" to start.</p>
                                    <button class="btn btn-sm btn-outline" onclick="window.GoalsComponent.openAddModal()">+ Add New Goal</button>
                                ` : goals.map(g => {
                                    const prog = streaks.calculateGoalProgress(g, store.state.history);
                                    const totalMilestones = (g.milestones || []).length;
                                    const completedMilestones = (g.milestones || []).filter(m => m.completed).length;
                                    return `
                                        <div class="goal-mini-row" onclick="window.GoalDetailComponent.open('${g.id}')">
                                            <div class="goal-mini-icon">🎯</div>
                                            <div class="goal-mini-info">
                                                <div class="goal-mini-title-row">
                                                    <span class="goal-mini-title">${g.title}</span>
                                                    <span class="goal-mini-percent">${prog}%</span>
                                                </div>
                                                <div class="mini-progress-track">
                                                    <div class="mini-progress-fill" style="width: ${prog}%;"></div>
                                                </div>
                                                <span class="goal-mini-sub">${completedMilestones}/${totalMilestones} milestones</span>
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    toggleTask(taskId) {
        if (!window.store) return;
        window.store.toggleTask(taskId);
        this.render();
    },

    promptQuickAddTask() {
        const title = prompt("Enter task title:");
        if (title && title.trim()) {
            const category = prompt("Category (DSA, Web Dev, Personal, Fitness, etc.):", "General") || "General";
            const duration = prompt("Duration (e.g. 30 min, 45 min):", "30 min") || "30 min";
            window.store.addTask({
                title: title.trim(),
                category: category.trim(),
                duration: duration.trim(),
                isToday: true
            });
            this.render();
        }
    }
};

window.DashboardComponent = DashboardComponent;
