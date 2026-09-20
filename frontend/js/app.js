/**
 * GoalMate Application Router (Simplified)
 * Handles navigation between Home, Goals, and Goal Detail views.
 */

const AppRouter = {
    currentRoute: 'home',

    init() {
        this.bindEvents();
        this.navigate('home');
        if (window.AICoach) window.AICoach.init();
    },

    navigate(route) {
        this.currentRoute = route;

        // Update active class on nav buttons
        document.querySelectorAll('.nav-item').forEach(el => {
            const r = el.getAttribute('data-route');
            el.classList.toggle('active', r === route);
        });

        // Close mobile sidebar if open
        const sidebar = document.getElementById('app-sidebar');
        if (sidebar) sidebar.classList.remove('sidebar-mobile-open');

        const coachPanel = document.getElementById('ai-coach-panel');

        if (route === 'home') {
            if (coachPanel) coachPanel.style.display = 'flex';
            if (window.DashboardComponent) window.DashboardComponent.render();
        } else if (route === 'goals') {
            if (coachPanel) coachPanel.style.display = 'none';
            if (window.GoalsComponent) window.GoalsComponent.render();
        } else if (route === 'goal-detail') {
            if (coachPanel) coachPanel.style.display = 'none';
            if (window.GoalDetailComponent) window.GoalDetailComponent.render();
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    bindEvents() {
        // Ctrl+K / Cmd+K search listener
        window.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                AppRouter.openSearchModal();
            } else if (e.key === 'Escape') {
                AppRouter.closeSearchModal();
            }
        });

        // Search bar click
        const searchInput = document.querySelector('.header-search-bar');
        if (searchInput) {
            searchInput.addEventListener('click', () => {
                AppRouter.openSearchModal();
            });
        }

        // Store state subscription
        if (window.store) {
            window.store.subscribe(() => {
                if (AppRouter.currentRoute === 'home' && window.DashboardComponent) {
                    window.DashboardComponent.render();
                }
            });
        }
    },

    toggleMobileSidebar() {
        const sidebar = document.getElementById('app-sidebar');
        if (sidebar) sidebar.classList.toggle('sidebar-mobile-open');
    },

    openSearchModal() {
        const modalContainer = document.getElementById('global-modal-container');
        if (!modalContainer) return;

        modalContainer.innerHTML = `
            <div class="modal-backdrop search-modal-backdrop" onclick="AppRouter.closeSearchModal()">
                <div class="search-modal-card" onclick="event.stopPropagation()">
                    <div class="search-input-header">
                        <span class="search-icon">🔍</span>
                        <input type="text" id="live-search-field" class="live-search-input" 
                            placeholder="Search your goals and milestones... (ESC to close)" 
                            autocomplete="off" autofocus />
                        <button class="search-esc-btn" onclick="AppRouter.closeSearchModal()">ESC</button>
                    </div>

                    <div id="search-results-list" class="search-results-container">
                        <div class="search-empty-prompt">Type to search your goals and milestones...</div>
                    </div>
                </div>
            </div>
        `;

        const field = document.getElementById('live-search-field');
        if (field) {
            field.focus();
            field.addEventListener('input', (e) => {
                AppRouter.executeSearch(e.target.value);
            });
        }
    },

    executeSearch(query) {
        const resultsContainer = document.getElementById('search-results-list');
        if (!resultsContainer) return;
        const q = (query || '').toLowerCase().trim();
        if (!q) {
            resultsContainer.innerHTML = `<div class="search-empty-prompt">Type to search your goals and milestones...</div>`;
            return;
        }

        const goals = window.store.getGoals();
        const matchedGoals = goals.filter(g => 
            g.title.toLowerCase().includes(q) || 
            (g.description && g.description.toLowerCase().includes(q)) ||
            (g.category && g.category.toLowerCase().includes(q))
        );

        if (matchedGoals.length === 0) {
            resultsContainer.innerHTML = `<div class="search-no-results">No goals found for "${query}"</div>`;
            return;
        }

        resultsContainer.innerHTML = `
            <div class="search-section-title">🎯 Goals (${matchedGoals.length})</div>
            ${matchedGoals.map(g => `
                <div class="search-result-row" onclick="AppRouter.jumpToGoal('${g.id}')">
                    <span class="res-badge cat-badge">${g.category}</span>
                    <strong class="res-title">${g.title}</strong>
                    <span class="res-sub">${g.description || ''}</span>
                </div>
            `).join('')}
        `;
    },

    jumpToGoal(goalId) {
        this.closeSearchModal();
        window.GoalDetailComponent.open(goalId);
    },

    closeSearchModal() {
        const modalContainer = document.getElementById('global-modal-container');
        if (!modalContainer) return;
        modalContainer.innerHTML = '';
    }
};

window.AppRouter = AppRouter;

document.addEventListener('DOMContentLoaded', () => {
    AppRouter.init();
});
