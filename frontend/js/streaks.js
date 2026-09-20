/**
 * GoalMate Streaks & Dynamic Analytics Engine
 * Provides accurate streak calculation, retroactive historical analysis,
 * dynamic progress calculation, and weekly chart breakdown data.
 */

const StreaksEngine = {
    // Format helper
    formatDate(d = new Date()) {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    // Get an array of past N dates in chronological order
    getPastDatesList(days = 14) {
        const list = [];
        for (let i = days - 1; i >= 0; i--) {
            const d = new Date();
            d.setDate(d.getDate() - i);
            list.push({
                dateStr: this.formatDate(d),
                dayName: d.toLocaleDateString('en-US', { weekday: 'short' }),
                dayNum: d.getDate(),
                monthName: d.toLocaleDateString('en-US', { month: 'short' }),
                isToday: i === 0
            });
        }
        return list;
    },

    // Calculate dynamic goal progress %
    // Based on milestones (60% weight) and consistency/logs (40% weight), or pure milestones if no logs
    calculateGoalProgress(goal, history = {}) {
        if (!goal) return 0;
        const milestones = goal.milestones || [];
        const totalM = milestones.length;
        const completedM = milestones.filter(m => m.completed).length;
        const milestoneRatio = totalM > 0 ? (completedM / totalM) : 0;

        // Historical completion in last 14 days
        const goalLogs = history[goal.id] || {};
        const recentDates = this.getPastDatesList(14);
        let loggedCount = 0;
        let completedDays = 0;
        recentDates.forEach(d => {
            const entry = goalLogs[d.dateStr];
            if (entry) {
                loggedCount++;
                if (entry.status === 'completed') completedDays++;
            }
        });

        if (totalM > 0 && loggedCount > 0) {
            const historyRatio = completedDays / Math.max(loggedCount, 7);
            const blended = Math.round((milestoneRatio * 0.6 + historyRatio * 0.4) * 100);
            return Math.min(100, Math.max(milestoneRatio > 0 ? 15 : 0, blended));
        } else if (totalM > 0) {
            return Math.round(milestoneRatio * 100);
        } else if (loggedCount > 0) {
            return Math.min(100, Math.round((completedDays / 14) * 100));
        }
        return 0;
    },

    // Calculate real streak for a goal (or aggregated across all goals)
    calculateStreak(goalId = null, history = {}) {
        const todayStr = this.formatDate();
        let currStreak = 0;
        let bestStreak = 0;
        let tempStreak = 0;

        // Check date sequence backwards up to 90 days
        const maxDays = 90;
        let activeConsecutive = true;

        for (let i = 0; i < maxDays; i++) {
            const d = new Date();
            d.setDate(d.getDate() - i);
            const dateStr = this.formatDate(d);

            let isCompleted = false;

            if (goalId) {
                const entry = (history[goalId] || {})[dateStr];
                isCompleted = entry && entry.status === 'completed';
            } else {
                // Aggregated streak: any goal completed or tasks completed that day
                let anyGoalCompleted = false;
                for (const gId in history) {
                    if (history[gId][dateStr] && history[gId][dateStr].status === 'completed') {
                        anyGoalCompleted = true;
                        break;
                    }
                }
                isCompleted = anyGoalCompleted;
            }

            if (isCompleted) {
                if (activeConsecutive) {
                    currStreak++;
                }
                tempStreak++;
                if (tempStreak > bestStreak) bestStreak = tempStreak;
            } else {
                // For day 0 (today), if not completed yet, don't break the streak yet if yesterday was completed
                if (i === 0) {
                    // Check yesterday
                    continue;
                } else {
                    activeConsecutive = false;
                    tempStreak = 0;
                }
            }
        }

        return {
            currentStreak: currStreak,
            bestStreak: Math.max(bestStreak, currStreak)
        };
    },

    // Calculate overview stats for dashboard
    calculateOverviewStats(store) {
        const goals = store.getGoals();
        const tasks = store.getTasks();
        const history = store.state.history || {};
        const todayStr = this.formatDate();

        // 1. Active Goals
        const activeGoalsCount = goals.length;

        // 2. Tasks Today
        const todayTasks = tasks.filter(t => t.isToday !== false);
        const completedTodayTasks = todayTasks.filter(t => t.completed).length;

        // 3. Current Streak
        const streakInfo = this.calculateStreak(null, history);

        // 4. Weekly Progress
        // % of tasks completed this week + days logged
        const past7Days = this.getPastDatesList(7);
        let totalPossible = 0;
        let totalAchieved = 0;

        past7Days.forEach(day => {
            let dayDone = false;
            for (const gId in history) {
                if (history[gId][day.dateStr] && history[gId][day.dateStr].status === 'completed') {
                    dayDone = true;
                    break;
                }
            }
            if (dayDone) {
                totalPossible += 1;
                totalAchieved += 1;
            }
        });

        const weekStart = past7Days[0].dateStr;
        const weekTasks = tasks.filter(t => t.dueDate >= weekStart && t.dueDate <= todayStr);
        totalPossible += weekTasks.length;
        totalAchieved += weekTasks.filter(t => t.completed).length;
        const weeklyProgress = totalPossible > 0
            ? Math.round((totalAchieved / totalPossible) * 100)
            : 0;

        return {
            activeGoals: activeGoalsCount,
            tasksTodayTotal: todayTasks.length,
            tasksTodayCompleted: completedTodayTasks,
            currentStreak: streakInfo.currentStreak,
            bestStreak: streakInfo.bestStreak,
            weeklyProgress: weeklyProgress
        };
    },

    // Days remaining till target date
    getDaysRemaining(targetDateStr) {
        if (!targetDateStr) return 0;
        const target = new Date(targetDateStr);
        const now = new Date();
        const diffTime = target - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return Math.max(0, diffDays);
    },

    // Generate weekly chart stacked bar data for Mon - Sun
    getWeeklyChartData(store) {
        const daysOrder = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const now = new Date();
        // Determine start of current week (Monday)
        const currentDayOfWeek = (now.getDay() + 6) % 7; // 0 = Mon, 6 = Sun
        
        const weekData = daysOrder.map((dayLabel, idx) => {
            const d = new Date(now);
            d.setDate(now.getDate() - currentDayOfWeek + idx);
            const dateStr = this.formatDate(d);
            const isPastOrToday = idx <= currentDayOfWeek;

            // Only render activity the user has actually logged. Each completed
            // task contributes one unit to its category for that date.
            let study = 0;
            let projects = 0;
            let personal = 0;
            let others = 0;
            const tasksOnDay = store.getTasks().filter(t => t.completed && t.dueDate === dateStr);
            tasksOnDay.forEach(task => {
                const category = (task.category || '').toLowerCase();
                if (/(study|school|college|exam|dsa|learn)/.test(category)) study++;
                else if (/(project|work|dev|portfolio|code)/.test(category)) projects++;
                else if (/(personal|health|fitness|habit)/.test(category)) personal++;
                else others++;
            });

            const total = study + projects + personal + others;
            return {
                day: dayLabel,
                dateStr,
                isToday: idx === currentDayOfWeek,
                isPastOrToday,
                study,
                projects,
                personal,
                others,
                totalHeightPercent: total > 0 ? Math.min(95, 25 + total * 15) : 0
            };
        });

        return weekData;
    }
};

window.StreaksEngine = StreaksEngine;
