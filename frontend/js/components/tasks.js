/**
 * GoalMate Tasks Page Component
 * Handles full task CRUD, completion toggle, goal assignment, category filters, and modal.
 */

const TasksComponent = {
    currentFilter: 'all', // 'all', 'today', 'pending', 'completed'
    selectedGoalId: 'all',
    selectedCategory: 'all',
    editingTaskId: null,

    render() {
        const store = window.store;
        if (!store) return;

        const container = document.getElementById('main-view-content');
        if (!container) return;

        const allTasks = store.getTasks();
        const goals = store.getGoals();
        const categories = ['all', ...new Set(allTasks.map(t => t.category))];

        let filtered = allTasks;

        // Tab filter
        if (this.currentFilter === 'today') {
            filtered = filtered.filter(t => t.isToday);
        } else if (this.currentFilter === 'pending') {
            filtered = filtered.filter(t => !t.completed);
        } else if (this.currentFilter === 'completed') {
            filtered = filtered.filter(t => t.completed);
        }

        // Goal filter
        if (this.selectedGoalId !== 'all') {
            filtered = filtered.filter(t => t.goalId === this.selectedGoalId);
        }

        // Category filter
        if (this.selectedCategory !== 'all') {
            filtered = filtered.filter(t => t.category === this.selectedCategory);
        }

        container.innerHTML = `
            <div class="view-page-wrapper">
                <div class="view-page-header flex-between">
                    <div>
                        <h2 class="view-page-title">☑️ Tasks Manager</h2>
                        <p class="view-page-subtitle">Organize your daily actionable steps, align them to your goals, and power through focus blocks.</p>
                    </div>
                    <button class="btn btn-primary" onclick="TasksComponent.openNewTaskModal()">
                        <span class="btn-icon">+</span> Add New Task
                    </button>
                </div>

                <!-- Filters & Controls Bar -->
                <div class="tasks-controls-card card">
                    <div class="filter-tabs-row">
                        <button class="filter-tab-btn ${this.currentFilter === 'all' ? 'active' : ''}" onclick="TasksComponent.setTab('all')">
                            All (${allTasks.length})
                        </button>
                        <button class="filter-tab-btn ${this.currentFilter === 'today' ? 'active' : ''}" onclick="TasksComponent.setTab('today')">
                            Today (${allTasks.filter(t => t.isToday).length})
                        </button>
                        <button class="filter-tab-btn ${this.currentFilter === 'pending' ? 'active' : ''}" onclick="TasksComponent.setTab('pending')">
                            Pending (${allTasks.filter(t => !t.completed).length})
                        </button>
                        <button class="filter-tab-btn ${this.currentFilter === 'completed' ? 'active' : ''}" onclick="TasksComponent.setTab('completed')">
                            Completed (${allTasks.filter(t => t.completed).length})
                        </button>
                    </div>

                    <div class="dropdown-filters-row">
                        <div class="filter-select-wrap">
                            <label class="select-label">Goal:</label>
                            <select class="form-select-sm" onchange="TasksComponent.setGoalFilter(this.value)">
                                <option value="all">All Goals</option>
                                ${goals.map(g => `
                                    <option value="${g.id}" ${this.selectedGoalId === g.id ? 'selected' : ''}>${g.title}</option>
                                `).join('')}
                            </select>
                        </div>

                        <div class="filter-select-wrap">
                            <label class="select-label">Category:</label>
                            <select class="form-select-sm" onchange="TasksComponent.setCategoryFilter(this.value)">
                                <option value="all">All Categories</option>
                                ${categories.filter(c => c !== 'all').map(c => `
                                    <option value="${c}" ${this.selectedCategory === c ? 'selected' : ''}>${c}</option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Tasks List -->
                ${filtered.length === 0 ? `
                    <div class="empty-state-card">
                        <div class="empty-icon">📝</div>
                        <h3>No tasks yet.</h3>
                        <p>No tasks match this filter. Create your next step and get rolling!</p>
                        <button class="btn btn-primary" onclick="TasksComponent.openNewTaskModal()">+ Add Task</button>
                    </div>
                ` : `
                    <div class="card tasks-list-card">
                        <div class="tasks-checklist">
                            ${filtered.map(t => {
                                const linkedGoal = goals.find(g => g.id === t.goalId);
                                return `
                                    <div class="task-row ${t.completed ? 'task-done' : ''}">
                                        <div class="task-checkbox-custom ${t.completed ? 'checked' : ''}" 
                                            onclick="TasksComponent.toggleTask('${t.id}')">
                                            ${t.completed ? '✓' : ''}
                                        </div>
                                        <div class="task-title-wrap" onclick="TasksComponent.toggleTask('${t.id}')">
                                            <span class="task-title-text">${t.title}</span>
                                            ${linkedGoal ? `
                                                <span class="task-goal-subtext">🎯 ${linkedGoal.title}</span>
                                            ` : ''}
                                        </div>
                                        <div class="task-meta-pills">
                                            <span class="category-pill pill-${t.category.toLowerCase().replace(/[^a-z]/g, '')}">${t.category}</span>
                                            <span class="duration-pill">⏱️ ${t.duration}</span>
                                            <span class="due-pill">📅 ${t.dueDate || 'Today'}</span>
                                        </div>
                                        <div class="task-actions-row">
                                            <button class="icon-btn-subtle" title="Edit Task" onclick="TasksComponent.openEditTaskModal('${t.id}')">✏️</button>
                                            <button class="icon-btn-subtle danger" title="Delete Task" onclick="TasksComponent.deleteTask('${t.id}')">🗑️</button>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `}
            </div>
        `;
    },

    setTab(tab) {
        this.currentFilter = tab;
        this.render();
    },

    setGoalFilter(goalId) {
        this.selectedGoalId = goalId;
        this.render();
    },

    setCategoryFilter(cat) {
        this.selectedCategory = cat;
        this.render();
    },

    toggleTask(taskId) {
        const task = window.store.toggleTask(taskId);
        if (task && task.completed && window.FocusTimer) {
            window.FocusTimer.playChime();
        }
        this.render();
        if (window.DashboardComponent) window.DashboardComponent.render();
    },

    deleteTask(taskId) {
        window.store.deleteTask(taskId);
        this.render();
        if (window.DashboardComponent) window.DashboardComponent.render();
    },

    openNewTaskModal() {
        this.editingTaskId = null;
        this.showTaskModal("Add New Task");
    },

    openEditTaskModal(taskId) {
        const task = window.store.getTasks().find(t => t.id === taskId);
        if (!task) return;
        this.editingTaskId = taskId;
        this.showTaskModal("Edit Task", task);
    },

    showTaskModal(titleText, taskData = null) {
        const modalContainer = document.getElementById('global-modal-container');
        if (!modalContainer) return;

        const goals = window.store.getGoals();

        modalContainer.innerHTML = `
            <div class="modal-backdrop" onclick="TasksComponent.closeModal()">
                <div class="modal-card" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h3 class="modal-title">${titleText}</h3>
                        <button class="modal-close-btn" onclick="TasksComponent.closeModal()">✕</button>
                    </div>

                    <form onsubmit="TasksComponent.saveTask(event)" class="modal-form">
                        <div class="form-group">
                            <label class="form-label">Task Title *</label>
                            <input type="text" id="task-title-input" class="form-input" required 
                                placeholder="e.g. Solve 3 DSA Problems on Trees" 
                                value="${taskData ? taskData.title : ''}" />
                        </div>

                        <div class="form-row-2">
                            <div class="form-group">
                                <label class="form-label">Assign to Goal</label>
                                <select id="task-goal-input" class="form-input">
                                    <option value="">-- No specific goal --</option>
                                    ${goals.map(g => `
                                        <option value="${g.id}" ${taskData && taskData.goalId === g.id ? 'selected' : ''}>${g.title}</option>
                                    `).join('')}
                                </select>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Category</label>
                                <select id="task-cat-input" class="form-input">
                                    <option value="DSA" ${taskData && taskData.category === 'DSA' ? 'selected' : ''}>DSA</option>
                                    <option value="Web Dev" ${taskData && taskData.category === 'Web Dev' ? 'selected' : ''}>Web Dev</option>
                                    <option value="Personal" ${taskData && taskData.category === 'Personal' ? 'selected' : ''}>Personal</option>
                                    <option value="Fitness" ${taskData && taskData.category === 'Fitness' ? 'selected' : ''}>Fitness</option>
                                    <option value="General" ${taskData && taskData.category === 'General' ? 'selected' : ''}>General</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-row-2">
                            <div class="form-group">
                                <label class="form-label">Estimated Duration</label>
                                <select id="task-dur-input" class="form-input">
                                    <option value="15 min" ${taskData && taskData.duration === '15 min' ? 'selected' : ''}>15 min</option>
                                    <option value="30 min" ${taskData && taskData.duration === '30 min' ? 'selected' : ''}>30 min</option>
                                    <option value="45 min" ${taskData && taskData.duration === '45 min' ? 'selected' : ''}>45 min</option>
                                    <option value="60 min" ${taskData && taskData.duration === '60 min' ? 'selected' : ''}>60 min</option>
                                    <option value="90 min" ${taskData && taskData.duration === '90 min' ? 'selected' : ''}>90 min</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label class="form-label">Due Date</label>
                                <input type="date" id="task-due-input" class="form-input" 
                                    value="${taskData ? taskData.dueDate : new Date().toISOString().split('T')[0]}" />
                            </div>
                        </div>

                        <div class="form-group checkbox-form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="task-today-input" ${!taskData || taskData.isToday ? 'checked' : ''} />
                                <span>Display in Today's Tasks on Dashboard</span>
                            </label>
                        </div>

                        <div class="modal-actions">
                            <button type="button" class="btn btn-outline" onclick="TasksComponent.closeModal()">Cancel</button>
                            <button type="submit" class="btn btn-primary">${taskData ? 'Save Changes' : 'Create Task'}</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    saveTask(e) {
        e.preventDefault();
        const title = document.getElementById('task-title-input').value.trim();
        const goalId = document.getElementById('task-goal-input').value;
        const category = document.getElementById('task-cat-input').value;
        const duration = document.getElementById('task-dur-input').value;
        const dueDate = document.getElementById('task-due-input').value;
        const isToday = document.getElementById('task-today-input').checked;

        if (!title) return;

        const payload = { title, goalId, category, duration, dueDate, isToday };

        if (this.editingTaskId) {
            window.store.updateTask(this.editingTaskId, payload);
        } else {
            window.store.addTask(payload);
        }

        this.closeModal();
        this.render();
        if (window.DashboardComponent) window.DashboardComponent.render();
    },

    closeModal() {
        const modalContainer = document.getElementById('global-modal-container');
        if (modalContainer) modalContainer.innerHTML = '';
    }
};

window.TasksComponent = TasksComponent;
