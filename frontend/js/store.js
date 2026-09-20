/**
 * GoalMate Store - Clean State (No Hardcoded/Pre-filled Data)
 * User creates their own goals, tasks, and historical logs.
 */

const STORAGE_KEY = 'goalmate_clean_slate_v2';

function formatDate(d = new Date()) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

const CLEAN_INITIAL_DATA = {
    user: {
        name: "",
        title: "Dream it. Plan it. Do it.",
        avatar: "/assets/images/hinata_avatar.jpg",
        aiPersona: "High Energy (Hinata)"
    },
    goals: [],
    tasks: [],
    history: {},
    recentActivity: []
};

class GoalMateStore {
    constructor() {
        this.listeners = [];
        this.load();
    }

    load() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                this.state = JSON.parse(raw);
                if (!this.state.goals) this.state.goals = [];
                if (!this.state.tasks) this.state.tasks = [];
                if (!this.state.history) this.state.history = {};
                if (!this.state.user) this.state.user = CLEAN_INITIAL_DATA.user;
                if (!this.state.recentActivity) this.state.recentActivity = [];
            } else {
                this.state = JSON.parse(JSON.stringify(CLEAN_INITIAL_DATA));
                this.save();
            }
        } catch (e) {
            console.error("Failed to load state from localStorage:", e);
            this.state = JSON.parse(JSON.stringify(CLEAN_INITIAL_DATA));
        }
    }

    save() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
            this.notify();
        } catch (e) {
            console.error("Failed to save state to localStorage:", e);
        }
    }

    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    notify() {
        this.listeners.forEach(l => {
            try { l(this.state); } catch (e) { console.error("Listener error:", e); }
        });
    }

    // User
    getUser() {
        return this.state.user || CLEAN_INITIAL_DATA.user;
    }

    updateUser(updates) {
        this.state.user = { ...this.state.user, ...updates };
        this.save();
    }

    // Goals
    getGoals() {
        return (this.state.goals || []).filter(g => !g.archived);
    }

    getGoal(id) {
        return (this.state.goals || []).find(g => g.id === id);
    }

    addGoal(goalData) {
        const id = 'goal-' + Date.now();
        const newGoal = {
            id,
            title: goalData.title || "New Goal",
            description: goalData.description || "",
            category: goalData.category || "General",
            frequency: goalData.frequency || "daily",
            targetDate: goalData.targetDate || formatDate(),
            coverImage: goalData.coverImage || "/assets/images/header_banner.png",
            milestones: goalData.milestones || [],
            createdAt: formatDate(),
            archived: false
        };
        if (!this.state.goals) this.state.goals = [];
        this.state.goals.unshift(newGoal);
        this.addActivity(`Created new goal: ${newGoal.title}`, "goal");
        this.save();
        return newGoal;
    }

    updateGoal(id, updates) {
        const index = this.state.goals.findIndex(g => g.id === id);
        if (index !== -1) {
            this.state.goals[index] = { ...this.state.goals[index], ...updates };
            this.addActivity(`Updated goal: ${this.state.goals[index].title}`, "goal");
            this.save();
            return this.state.goals[index];
        }
        return null;
    }

    deleteGoal(id) {
        const goal = this.getGoal(id);
        const title = goal ? goal.title : "Goal";
        this.state.goals = this.state.goals.filter(g => g.id !== id);
        this.state.tasks = (this.state.tasks || []).filter(t => t.goalId !== id);
        if (this.state.history) delete this.state.history[id];
        this.addActivity(`Deleted goal: ${title}`, "goal");
        this.save();
    }

    toggleMilestone(goalId, milestoneId) {
        const goal = this.getGoal(goalId);
        if (!goal || !goal.milestones) return;
        const milestone = goal.milestones.find(m => m.id === milestoneId);
        if (milestone) {
            milestone.completed = !milestone.completed;
            this.addActivity(`${milestone.completed ? 'Completed' : 'Unchecked'} milestone: ${milestone.title}`, "milestone");
            this.save();
        }
    }

    addMilestone(goalId, title) {
        const goal = this.getGoal(goalId);
        if (!goal || !title.trim()) return;
        if (!goal.milestones) goal.milestones = [];
        const newMilestone = {
            id: 'm-' + Date.now(),
            title: title.trim(),
            completed: false
        };
        goal.milestones.push(newMilestone);
        this.addActivity(`Added milestone: ${newMilestone.title}`, "milestone");
        this.save();
    }

    deleteMilestone(goalId, milestoneId) {
        const goal = this.getGoal(goalId);
        if (!goal || !goal.milestones) return;
        goal.milestones = goal.milestones.filter(m => m.id !== milestoneId);
        this.save();
    }

    // Retroactive Date History Tracking
    getGoalHistory(goalId) {
        if (!this.state.history) this.state.history = {};
        if (!this.state.history[goalId]) {
            this.state.history[goalId] = {};
        }
        return this.state.history[goalId];
    }

    setGoalDateStatus(goalId, dateStr, status, note = "") {
        if (!this.state.history) this.state.history = {};
        if (!this.state.history[goalId]) {
            this.state.history[goalId] = {};
        }
        this.state.history[goalId][dateStr] = {
            status,
            note: note.trim(),
            updatedAt: new Date().toISOString()
        };
        const goal = this.getGoal(goalId);
        const goalTitle = goal ? goal.title : "Goal";
        this.addActivity(`Updated progress for ${dateStr} (${status}) on ${goalTitle}`, "streak");
        this.save();
    }

    // Tasks
    getTasks() {
        return this.state.tasks || [];
    }

    getTodayTasks() {
        return (this.state.tasks || []).filter(t => t.isToday !== false);
    }

    addTask(taskData) {
        const newTask = {
            id: 't-' + Date.now(),
            goalId: taskData.goalId || "",
            title: taskData.title || "New Task",
            category: taskData.category || "General",
            duration: taskData.duration || "30 min",
            dueDate: taskData.dueDate || formatDate(),
            completed: false,
            isToday: taskData.isToday !== undefined ? taskData.isToday : true
        };
        if (!this.state.tasks) this.state.tasks = [];
        this.state.tasks.push(newTask);
        this.addActivity(`Added task: ${newTask.title}`, "task");
        this.save();
        return newTask;
    }

    toggleTask(id) {
        const task = (this.state.tasks || []).find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            this.addActivity(`${task.completed ? 'Completed' : 'Uncompleted'} task: ${task.title}`, "task");
            
            // If completed and tied to a goal, also register today's progress for that goal
            if (task.completed && task.goalId) {
                const today = formatDate();
                if (!this.state.history) this.state.history = {};
                if (!this.state.history[task.goalId]) this.state.history[task.goalId] = {};
                this.state.history[task.goalId][today] = {
                    status: 'completed',
                    note: `Completed task: ${task.title}`,
                    updatedAt: new Date().toISOString()
                };
            }
            this.save();
            return task;
        }
        return null;
    }

    deleteTask(id) {
        const task = (this.state.tasks || []).find(t => t.id === id);
        const title = task ? task.title : "Task";
        this.state.tasks = (this.state.tasks || []).filter(t => t.id !== id);
        this.addActivity(`Deleted task: ${title}`, "task");
        this.save();
    }

    // Activity Stream
    addActivity(text, type = "general") {
        if (!this.state.recentActivity) this.state.recentActivity = [];
        const newAct = {
            id: 'a-' + Date.now(),
            text,
            timeAgo: "Just now",
            type,
            timestamp: Date.now()
        };
        this.state.recentActivity.unshift(newAct);
        if (this.state.recentActivity.length > 15) {
            this.state.recentActivity = this.state.recentActivity.slice(0, 15);
        }
    }

    getRecentActivity() {
        return this.state.recentActivity || [];
    }

    resetToDefaults() {
        this.state = JSON.parse(JSON.stringify(CLEAN_INITIAL_DATA));
        this.save();
    }
}

window.store = new GoalMateStore();
