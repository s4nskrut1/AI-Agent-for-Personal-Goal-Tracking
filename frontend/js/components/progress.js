/**
 * GoalMate Progress Page Component
 * Renders comprehensive analytics, 60-day habit heatmap, goal breakdowns,
 * and quick retroactive date logging.
 */

const ProgressComponent = {
    selectedGoalId: 'all',

    render() {
        const store = window.store;
        const streaks = window.StreaksEngine;
        if (!store || !streaks) return;

        const container = document.getElementById('main-view-content');
        if (!container) return;

        const stats = streaks.calculateOverviewStats(store);
        const goals = store.getGoals();
        const history = store.state.history || {};

        // 60-day heatmap data
        const past60Days = streaks.getPastDatesList(60);

        container.innerHTML = `
            <div class="view-page-wrapper">
                <div class="view-page-header flex-between">
                    <div>
                        <h2 class="view-page-title">📈 Analytics & Progress</h2>
                        <p class="view-page-subtitle">Track your consistency trends, habit heatmap, and deep work output across all goals.</p>
                    </div>
                </div>

                <!-- 4 KPI Cards -->
                <div class="stats-grid">
                    <div class="card stat-card stat-orange">
                        <div class="stat-icon-wrap bg-orange-light"><span class="stat-emoji">🎯</span></div>
                        <div class="stat-info">
                            <span class="stat-value">${stats.activeGoals}</span>
                            <span class="stat-label">Active Goals Tracked</span>
                        </div>
                    </div>
                    <div class="card stat-card stat-flame">
                        <div class="stat-icon-wrap bg-flame-light"><span class="stat-emoji">🔥</span></div>
                        <div class="stat-info">
                            <span class="stat-value">${stats.currentStreak} Days</span>
                            <span class="stat-label">Active Streak (Best: ${stats.bestStreak}d)</span>
                        </div>
                    </div>
                    <div class="card stat-card stat-green">
                        <div class="stat-icon-wrap bg-green-light"><span class="stat-emoji">⚡</span></div>
                        <div class="stat-info">
                            <span class="stat-value">${stats.weeklyProgress}%</span>
                            <span class="stat-label">Weekly Consistency</span>
                        </div>
                    </div>
                    <div class="card stat-card stat-blue">
                        <div class="stat-icon-wrap bg-blue-light"><span class="stat-emoji">⏱️</span></div>
                        <div class="stat-info">
                            <span class="stat-value">${(store.state.focusSessions || []).length * 45}m</span>
                            <span class="stat-label">Deep Work Logged</span>
                        </div>
                    </div>
                </div>

                <!-- 60-Day Habit Activity Heatmap -->
                <div class="card progress-heatmap-card">
                    <div class="card-header flex-between">
                        <div>
                            <span class="card-title"><span class="icon">🗓️</span> 60-Day Habit Consistency Heatmap</span>
                            <p class="card-subtitle-sub">Hover or click any square to see details or modify historical logs.</p>
                        </div>
                        <div class="heatmap-legend">
                            <span class="hm-leg-label">Less</span>
                            <span class="hm-cell lvl-0"></span>
                            <span class="hm-cell lvl-1"></span>
                            <span class="hm-cell lvl-2"></span>
                            <span class="hm-cell lvl-3"></span>
                            <span class="hm-leg-label">More</span>
                        </div>
                    </div>

                    <div class="heatmap-grid-scroll">
                        <div class="heatmap-cells-grid">
                            ${past60Days.map(item => {
                                // Count how many goals had activity on this date
                                let count = 0;
                                for (const gId in history) {
                                    if (history[gId][item.dateStr] && history[gId][item.dateStr].status === 'completed') {
                                        count++;
                                    }
                                }
                                let lvl = 0;
                                if (count === 1) lvl = 1;
                                else if (count === 2) lvl = 2;
                                else if (count >= 3) lvl = 3;

                                return `
                                    <div class="hm-cell lvl-${lvl} ${item.isToday ? 'hm-today' : ''}" 
                                        title="${item.dateStr}: ${count} completed goals/habits"
                                        onclick="ProgressComponent.quickLogDate('${item.dateStr}')">
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                </div>

                <!-- Goal Breakdown Cards -->
                <div class="card goal-breakdown-card">
                    <div class="card-header flex-between">
                        <span class="card-title"><span class="icon">🎯</span> Goal Completion Breakdown</span>
                    </div>

                    <div class="goal-breakdown-table">
                        ${goals.map(g => {
                            const prog = streaks.calculateGoalProgress(g, history);
                            const gStreak = streaks.calculateStreak(g.id, history);
                            const daysLeft = streaks.getDaysRemaining(g.targetDate);
                            const completedM = (g.milestones || []).filter(m => m.completed).length;
                            const totalM = (g.milestones || []).length;

                            return `
                                <div class="breakdown-row" onclick="window.GoalDetailComponent.open('${g.id}')">
                                    <div class="b-col b-title-col">
                                        <strong class="b-title">${g.title}</strong>
                                        <span class="b-cat-pill">${g.category}</span>
                                    </div>
                                    <div class="b-col b-progress-col">
                                        <div class="b-prog-track">
                                            <div class="b-prog-fill orange-gradient" style="width: ${prog}%;"></div>
                                        </div>
                                        <span class="b-prog-num">${prog}%</span>
                                    </div>
                                    <div class="b-col b-meta-col">
                                        <span>📌 ${completedM}/${totalM} milestones</span>
                                    </div>
                                    <div class="b-col b-streak-col">
                                        <span>🔥 ${gStreak.currentStreak}d streak</span>
                                    </div>
                                    <div class="b-col b-action-col">
                                        <button class="btn btn-xs btn-outline">Details & History →</button>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
    },

    quickLogDate(dateStr) {
        const goals = window.store.getGoals();
        if (goals.length > 0) {
            window.GoalDetailComponent.currentGoalId = goals[0].id;
            window.GoalDetailComponent.openDateEditorModal(dateStr);
        }
    }
};

window.ProgressComponent = ProgressComponent;
