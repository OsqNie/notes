// Global State
let currentPage = 'dashboard';
let currentFilter = 'all';
let currentView = 'list';
let tasks = [];
let notes = [];
let projects = [];
let stats = {};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

// Initialize the application
function initializeApp() {
    // Set up keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Update keyboard shortcut display for platform
    updateKeyboardShortcutDisplay();
    
    // Set up navigation
    setupNavigation();
    
    // Set up theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.className = savedTheme + '-theme';
    updateThemeIcon();
}

// Set up event listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const page = e.target.getAttribute('data-page');
            showPage(page);
        });
    });
    
    // Filter chips
    document.querySelectorAll('.filter-chip').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const filter = e.target.getAttribute('data-filter');
            setTaskFilter(filter);
        });
    });
    
    // View switchers
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const view = e.target.getAttribute('data-view');
            setView(view, e.target.closest('.view-switcher'));
        });
    });
    
    // Priority selectors in modals
    document.querySelectorAll('.priority-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const container = e.target.closest('.priority-selector');
            container.querySelectorAll('.priority-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
        });
    });
    
    // Global search
    const searchInput = document.getElementById('global-search-input');
    searchInput.addEventListener('input', debounce(performGlobalSearch, 300));
    
    // Modal close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                hideModal(overlay.id);
            }
        });
    });
}

// Keyboard shortcuts
function handleKeyboardShortcuts(e) {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const cmdKey = isMac ? e.metaKey : e.ctrlKey;
    
    // Global search (Ctrl/Cmd + K)
    if (cmdKey && e.key === 'k') {
        e.preventDefault();
        document.getElementById('global-search-input').focus();
    }
    
    // New task (Ctrl/Cmd + N)
    if (cmdKey && e.key === 'n' && !e.shiftKey) {
        e.preventDefault();
        showCreateTaskModal();
    }
    
    // New note (Ctrl/Cmd + Shift + N)
    if (cmdKey && e.shiftKey && e.key === 'N') {
        e.preventDefault();
        showCreateNoteModal();
    }
    
    // New project (Ctrl/Cmd + Shift + P)
    if (cmdKey && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        showCreateProjectModal();
    }
    
    // Save current modal (Ctrl/Cmd + S)
    if (cmdKey && e.key === 's') {
        e.preventDefault();
        handleSaveShortcut();
    }
    
    // Save and new (Ctrl/Cmd + Shift + S)
    if (cmdKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        handleSaveAndNewShortcut();
    }
    
    // Toggle theme (Ctrl/Cmd + Shift + T)
    if (cmdKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        toggleTheme();
    }
    
    // Navigate to Dashboard (Ctrl/Cmd + 1)
    if (cmdKey && e.key === '1') {
        e.preventDefault();
        showPage('dashboard');
    }
    
    // Navigate to Tasks (Ctrl/Cmd + 2)
    if (cmdKey && e.key === '2') {
        e.preventDefault();
        showPage('tasks');
    }
    
    // Navigate to Notes (Ctrl/Cmd + 3)
    if (cmdKey && e.key === '3') {
        e.preventDefault();
        showPage('notes');
    }
    
    // Navigate to Projects (Ctrl/Cmd + 4)
    if (cmdKey && e.key === '4') {
        e.preventDefault();
        showPage('projects');
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            hideModal(modal.id);
        });
    }
    
    // Enter to submit forms in modals
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        const activeModal = document.querySelector('.modal-overlay.active');
        if (activeModal) {
            e.preventDefault();
            handleModalSubmit(activeModal);
        }
    }
}

// Navigation
function setupNavigation() {
    showPage('dashboard');
}

function showPage(pageName) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-page') === pageName) {
            btn.classList.add('active');
        }
    });
    
    // Update pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    const targetPage = document.getElementById(pageName);
    if (targetPage) {
        targetPage.classList.add('active');
        targetPage.classList.add('fade-in');
    }
    
    currentPage = pageName;
    
    // Load page-specific data
    switch (pageName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'tasks':
            loadTasks();
            break;
        case 'notes':
            loadNotes();
            break;
        case 'projects':
            loadProjects();
            break;
    }
}

// Data loading functions
async function loadInitialData() {
    try {
        await Promise.all([
            loadStats(),
            loadDashboardData()
        ]);
    } catch (error) {
        console.error('Error loading initial data:', error);
        showError('Failed to load initial data');
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        stats = await response.json();
        updateStatsDisplay();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStatsDisplay() {
    document.getElementById('due-today-count').textContent = stats.tasks?.due_today || 0;
    document.getElementById('active-tasks-count').textContent = stats.tasks?.pending + stats.tasks?.in_progress || 0;
    document.getElementById('projects-count').textContent = stats.packages?.total || 0;
    document.getElementById('notes-count').textContent = stats.notes?.total || 0;
    
    // Update filter counts
    document.getElementById('all-count').textContent = stats.tasks?.total || 0;
    document.getElementById('pending-count').textContent = stats.tasks?.pending || 0;
    document.getElementById('progress-count').textContent = stats.tasks?.in_progress || 0;
    document.getElementById('completed-count').textContent = stats.tasks?.completed || 0;
}

async function loadDashboardData() {
    try {
        const [tasksResponse, notesResponse, projectsResponse] = await Promise.all([
            fetch('/api/tasks?limit=5'),
            fetch('/api/notes?limit=3'),
            fetch('/api/packages?limit=3')
        ]);
        
        const todayTasks = await tasksResponse.json();
        const recentNotes = await notesResponse.json();
        const projectProgress = await projectsResponse.json();
        
        renderDashboardTasks(todayTasks);
        renderDashboardNotes(recentNotes);
        renderDashboardProjects(projectProgress);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
        showError('Failed to load tasks');
    }
}

async function loadNotes() {
    try {
        const response = await fetch('/api/notes');
        notes = await response.json();
        renderNotes();
    } catch (error) {
        console.error('Error loading notes:', error);
        showError('Failed to load notes');
    }
}

async function loadProjects() {
    try {
        const response = await fetch('/api/packages');
        projects = await response.json();
        renderProjects();
        updateProjectSelectors();
    } catch (error) {
        console.error('Error loading projects:', error);
        showError('Failed to load projects');
    }
}

// Rendering functions
function renderDashboardTasks(tasks) {
    const container = document.getElementById('today-tasks');
    
    if (!tasks || tasks.length === 0) {
        container.innerHTML = '<div class="empty-state">No tasks due today</div>';
        return;
    }
    
    container.innerHTML = tasks.slice(0, 5).map(task => `
        <div class="task-item-preview" data-priority="${task.priority}">
            <div class="task-checkbox">
                <input type="checkbox" ${task.status === 'completed' ? 'checked' : ''} 
                       onchange="toggleTaskStatus('${task.id}')">
            </div>
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    <span class="priority-indicator priority-${task.priority}">${task.priority}</span>
                    ${task.due_date ? `<span class="due-date">${formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function renderDashboardNotes(notes) {
    const container = document.getElementById('recent-notes');
    
    if (!notes || notes.length === 0) {
        container.innerHTML = '<div class="empty-state">No recent notes</div>';
        return;
    }
    
    container.innerHTML = notes.slice(0, 3).map(note => `
        <div class="note-item-preview" onclick="openNote('${note.id}')">
            <div class="note-title">${escapeHtml(note.title)}</div>
            <div class="note-preview">${escapeHtml(note.content).substring(0, 100)}...</div>
            <div class="note-date">${formatDate(note.updated_at)}</div>
        </div>
    `).join('');
}

function renderDashboardProjects(projects) {
    const container = document.getElementById('project-progress');
    
    if (!projects || projects.length === 0) {
        container.innerHTML = '<div class="empty-state">No active projects</div>';
        return;
    }
    
    container.innerHTML = projects.slice(0, 3).map(project => {
        const progress = calculateProjectProgress(project);
        return `
            <div class="project-progress-item">
                <div class="project-name">${escapeHtml(project.name)}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
                <div class="progress-text">${progress}% complete</div>
            </div>
        `;
    }).join('');
}

function renderTasks() {
    const container = document.getElementById('task-list');
    let filteredTasks = filterTasks(tasks);
    
    if (filteredTasks.length === 0) {
        container.innerHTML = '<div class="empty-state">No tasks found</div>';
        return;
    }
    
    // Sort tasks: completed items go to bottom
    const sortedTasks = [...filteredTasks].sort((a, b) => {
        if (a.status === 'completed' && b.status !== 'completed') return 1;
        if (a.status !== 'completed' && b.status === 'completed') return -1;
        
        // Secondary sort by due date
        if (a.due_date && b.due_date) {
            return new Date(a.due_date) - new Date(b.due_date);
        }
        if (a.due_date && !b.due_date) return -1;
        if (!a.due_date && b.due_date) return 1;
        
        return 0;
    });
    
    if (currentView === 'board') {
        renderTasksBoard(sortedTasks, container);
    } else {
        renderTasksList(sortedTasks, container);
    }
}

function renderTasksList(tasks, container) {
    container.className = 'task-list';
    container.innerHTML = tasks.map(task => `
        <div class="task-item ${task.status === 'completed' ? 'completed' : ''}" data-priority="${task.priority}">
            <div class="task-checkbox">
                <input type="checkbox" id="task-${task.id}" ${task.status === 'completed' ? 'checked' : ''} 
                       onchange="toggleTaskStatus('${task.id}')">
                <label for="task-${task.id}"></label>
            </div>
            
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    ${task.package_id ? `<span class="task-project">${getProjectName(task.package_id)}</span>` : ''}
                    ${task.due_date ? `<span class="task-due">${formatDueDate(task.due_date)}</span>` : ''}
                    <div class="task-tags">
                        ${task.tags ? task.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('') : ''}
                    </div>
                </div>
            </div>
            
            <div class="task-actions">
                <button class="action-btn" onclick="editTask('${task.id}')" title="Edit">✏️</button>
                <button class="action-btn" onclick="deleteTask('${task.id}')" title="Delete">🗑️</button>
            </div>
            
            <div class="task-priority priority-${task.priority}"></div>
        </div>
    `).join('');
}

function renderTasksBoard(tasks, container) {
    container.className = 'task-board';
    
    const statusColumns = {
        'pending': { title: 'To Do', tasks: [] },
        'in-progress': { title: 'In Progress', tasks: [] },
        'completed': { title: 'Done', tasks: [] }
    };
    
    // Group tasks by status
    tasks.forEach(task => {
        const status = task.status === 'cancelled' ? 'completed' : task.status;
        if (statusColumns[status]) {
            statusColumns[status].tasks.push(task);
        }
    });
    
    container.innerHTML = Object.entries(statusColumns).map(([status, column]) => `
        <div class="board-column" data-status="${status}">
            <div class="column-header">
                <h3>${column.title}</h3>
                <span class="task-count">${column.tasks.length}</span>
            </div>
            <div class="column-tasks">
                ${column.tasks.map(task => `
                    <div class="task-card" data-priority="${task.priority}">
                        <div class="task-card-header">
                            <div class="task-title">${escapeHtml(task.title)}</div>
                            <div class="task-actions">
                                <button class="action-btn" onclick="editTask('${task.id}')" title="Edit">✏️</button>
                                <button class="action-btn" onclick="deleteTask('${task.id}')" title="Delete">🗑️</button>
                            </div>
                        </div>
                        ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                        <div class="task-meta">
                            ${task.package_id ? `<span class="task-project">${getProjectName(task.package_id)}</span>` : ''}
                            ${task.due_date ? `<span class="task-due">${formatDueDate(task.due_date)}</span>` : ''}
                        </div>
                        <div class="task-tags">
                            ${task.tags ? task.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('') : ''}
                        </div>
                        <div class="priority-indicator priority-${task.priority}"></div>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

function renderNotes() {
    const container = document.getElementById('notes-grid');
    
    if (notes.length === 0) {
        container.innerHTML = '<div class="empty-state">No notes found</div>';
        return;
    }
    
    container.innerHTML = notes.map(note => `
        <div class="note-card" onclick="openNote('${note.id}')">
            <div class="note-header">
                <h4 class="note-title">${escapeHtml(note.title)}</h4>
                <div class="note-actions">
                    <button class="action-btn" onclick="event.stopPropagation(); editNote('${note.id}')" title="Edit">✏️</button>
                    <button class="action-btn" onclick="event.stopPropagation(); deleteNote('${note.id}')" title="Delete">🗑️</button>
                </div>
            </div>
            
            <div class="note-preview">
                ${escapeHtml(note.content).substring(0, 150)}${note.content.length > 150 ? '...' : ''}
            </div>
            
            <div class="note-footer">
                <div class="note-tags">
                    ${note.tags ? note.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('') : ''}
                </div>
                <div class="note-meta">
                    <span class="note-date">${formatDate(note.updated_at)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderProjects() {
    const container = document.getElementById('projects-grid');
    
    if (projects.length === 0) {
        container.innerHTML = '<div class="empty-state">No projects found</div>';
        return;
    }
    
    container.innerHTML = projects.map(project => {
        const progress = calculateProjectProgress(project);
        return `
            <div class="project-card">
                <div class="project-header">
                    <div class="project-icon">📁</div>
                    <div class="project-info">
                        <h3 class="project-title">${escapeHtml(project.name)}</h3>
                        <p class="project-description">${escapeHtml(project.description || '')}</p>
                    </div>
                    <div class="project-status status-${project.status}">${project.status}</div>
                </div>
                
                <div class="project-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <div class="progress-text">
                        <span>Progress</span>
                        <span>${progress}%</span>
                    </div>
                </div>
                
                <div class="project-meta">
                    ${project.due_date ? `<div class="project-due">Due: ${formatDate(project.due_date)}</div>` : ''}
                </div>
                
                <div class="project-actions">
                    <button class="action-btn" onclick="viewProject('${project.id}')">View Tasks</button>
                    <button class="action-btn" onclick="editProject('${project.id}')">Edit</button>
                    <button class="action-btn" onclick="deleteProject('${project.id}')">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

// Filter and utility functions
function filterTasks(tasks) {
    if (currentFilter === 'all') return tasks;
    return tasks.filter(task => task.status === currentFilter);
}

function setTaskFilter(filter) {
    currentFilter = filter;
    
    // Update active filter chip
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.classList.remove('active');
        if (chip.getAttribute('data-filter') === filter) {
            chip.classList.add('active');
        }
    });
    
    renderTasks();
}

function setView(view, container) {
    container.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-view') === view) {
            btn.classList.add('active');
        }
    });
    
    currentView = view;
    
    // Re-render tasks with new view
    if (currentPage === 'tasks') {
        renderTasks();
    }
}

// Modal functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        // Focus first input
        const firstInput = modal.querySelector('input, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        // Clear form data
        const form = modal.querySelector('.modal-body');
        if (form) {
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (input.type !== 'button') {
                    input.value = '';
                }
            });
            // Reset priority selector
            const priorityBtns = form.querySelectorAll('.priority-btn');
            priorityBtns.forEach(btn => btn.classList.remove('active'));
            const defaultPriority = form.querySelector('.priority-btn[data-priority="medium"]');
            if (defaultPriority) defaultPriority.classList.add('active');
        }
        
        // Reset modal state based on type
        switch (modalId) {
            case 'task-modal':
                resetTaskModal();
                break;
            case 'note-modal':
                resetNoteModal();
                break;
            case 'project-modal':
                resetProjectModal();
                break;
        }
    }
}

function showCreateTaskModal() {
    showModal('task-modal');
}

function showCreateNoteModal() {
    showModal('note-modal');
}

function showCreateProjectModal() {
    showModal('project-modal');
}

// CRUD operations
async function createTask(saveAndNew = false) {
    const title = document.getElementById('task-title').value.trim();
    if (!title) {
        showError('Task title is required');
        return;
    }
    
    const priority = document.querySelector('.priority-btn.active')?.getAttribute('data-priority') || 'medium';
    const dueDate = document.getElementById('task-due-date').value;
    const projectId = document.getElementById('task-project').value;
    const description = document.getElementById('task-description').value.trim();
    const tags = document.getElementById('task-tags').value.split(',').map(tag => tag.trim()).filter(Boolean);
    
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                description: description || null,
                priority,
                due_date: dueDate || null,
                package_id: projectId || null,
                tags
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create task');
        }
        
        if (saveAndNew) {
            // Clear form but keep modal open
            clearTaskForm();
            showSuccess('Task created! Ready for next task.');
        } else {
            hideModal('task-modal');
            showSuccess('Task created successfully');
        }
        
        // Reload data
        await Promise.all([loadStats(), loadTasks()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showError('Failed to create task');
    }
}

async function createNote(saveAndNew = false) {
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    
    if (!title) {
        showError('Note title is required');
        return;
    }
    
    const projectId = document.getElementById('note-project').value;
    const tags = document.getElementById('note-tags').value.split(',').map(tag => tag.trim()).filter(Boolean);
    
    try {
        const response = await fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                content: content || '',
                package_id: projectId || null,
                tags
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create note');
        }
        
        if (saveAndNew) {
            // Clear form but keep modal open
            clearNoteForm();
            showSuccess('Note created! Ready for next note.');
        } else {
            hideModal('note-modal');
            showSuccess('Note created successfully');
        }
        
        // Reload data
        await Promise.all([loadStats(), loadNotes()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error creating note:', error);
        showError('Failed to create note');
    }
}

async function createProject(saveAndNew = false) {
    const name = document.getElementById('project-name').value.trim();
    
    if (!name) {
        showError('Project name is required');
        return;
    }
    
    const description = document.getElementById('project-description').value.trim();
    const dueDate = document.getElementById('project-due-date').value;
    
    try {
        const response = await fetch('/api/packages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                description: description || null,
                due_date: dueDate || null
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create project');
        }
        
        if (saveAndNew) {
            // Clear form but keep modal open
            clearProjectForm();
            showSuccess('Project created! Ready for next project.');
        } else {
            hideModal('project-modal');
            showSuccess('Project created successfully');
        }
        
        // Reload data
        await Promise.all([loadStats(), loadProjects()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error creating project:', error);
        showError('Failed to create project');
    }
}

async function toggleTaskStatus(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: newStatus
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update task');
        }
        
        // Update local state
        task.status = newStatus;
        
        // Add completion animation if completed
        if (newStatus === 'completed') {
            const taskElement = document.querySelector(`input[onchange*="${taskId}"]`).closest('.task-item');
            if (taskElement) {
                taskElement.classList.add('task-complete-animation');
                setTimeout(() => {
                    taskElement.classList.remove('task-complete-animation');
                }, 500);
            }
        }
        
        // Reload stats and re-render
        await loadStats();
        renderTasks();
        
    } catch (error) {
        console.error('Error updating task:', error);
        showError('Failed to update task');
        // Revert checkbox state
        const checkbox = document.querySelector(`input[onchange*="${taskId}"]`);
        if (checkbox) {
            checkbox.checked = task.status === 'completed';
        }
    }
}

// Search functionality
async function performGlobalSearch() {
    const query = document.getElementById('global-search-input').value.trim();
    if (!query) return;
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        showSearchResults(query, results);
    } catch (error) {
        console.error('Error performing search:', error);
        showError('Search failed');
    }
}

function showSearchResults(query, results) {
    // Create or show search results modal
    let searchModal = document.getElementById('search-results-modal');
    if (!searchModal) {
        searchModal = createSearchResultsModal();
        document.body.appendChild(searchModal);
    }
    
    const totalResults = results.tasks.length + results.notes.length + results.packages.length;
    
    // Update modal content
    const title = searchModal.querySelector('.modal-header h3');
    title.textContent = `Search Results for "${query}" (${totalResults} results)`;
    
    const content = searchModal.querySelector('.search-results-content');
    content.innerHTML = '';
    
    if (totalResults === 0) {
        content.innerHTML = '<div class="empty-state">No results found</div>';
    } else {
        // Add tasks section
        if (results.tasks.length > 0) {
            content.appendChild(createSearchSection('Tasks', results.tasks, 'task'));
        }
        
        // Add notes section
        if (results.notes.length > 0) {
            content.appendChild(createSearchSection('Notes', results.notes, 'note'));
        }
        
        // Add packages section
        if (results.packages.length > 0) {
            content.appendChild(createSearchSection('Projects', results.packages, 'package'));
        }
    }
    
    // Show modal
    searchModal.classList.add('active');
}

function createSearchResultsModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'search-results-modal';
    modal.innerHTML = `
        <div class="modal search-modal">
            <div class="modal-header">
                <h3>Search Results</h3>
                <button class="modal-close" onclick="hideModal('search-results-modal')">×</button>
            </div>
            <div class="modal-body">
                <div class="search-results-content"></div>
            </div>
        </div>
    `;
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            hideModal('search-results-modal');
        }
    });
    
    return modal;
}

function createSearchSection(title, items, type) {
    const section = document.createElement('div');
    section.className = 'search-section';
    
    const header = document.createElement('h4');
    header.className = 'search-section-title';
    header.textContent = `${title} (${items.length})`;
    section.appendChild(header);
    
    const list = document.createElement('div');
    list.className = 'search-results-list';
    
    items.forEach(item => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        resultItem.onclick = () => handleSearchResultClick(item, type);
        
        let content = '';
        if (type === 'task') {
            const priorityClass = `priority-${item.priority}`;
            const statusClass = `status-${item.status}`;
            content = `
                <div class="result-header">
                    <div class="result-title">${escapeHtml(item.title)}</div>
                    <div class="result-badges">
                        <span class="priority-badge ${priorityClass}">${item.priority}</span>
                        <span class="status-badge ${statusClass}">${item.status}</span>
                    </div>
                </div>
                ${item.description ? `<div class="result-description">${escapeHtml(item.description)}</div>` : ''}
                <div class="result-meta">
                    ${item.due_date ? `Due: ${formatDate(item.due_date)} • ` : ''}
                    ${item.package_id ? `Project: ${getProjectName(item.package_id)} • ` : ''}
                    ID: ${item.id.substring(0, 8)}
                </div>
            `;
        } else if (type === 'note') {
            content = `
                <div class="result-header">
                    <div class="result-title">${escapeHtml(item.title)}</div>
                </div>
                ${item.content ? `<div class="result-description">${escapeHtml(item.content.substring(0, 150))}${item.content.length > 150 ? '...' : ''}</div>` : ''}
                <div class="result-meta">
                    Updated: ${formatDate(item.updated_at)} • 
                    ${item.package_id ? `Project: ${getProjectName(item.package_id)} • ` : ''}
                    ID: ${item.id.substring(0, 8)}
                </div>
            `;
        } else if (type === 'package') {
            content = `
                <div class="result-header">
                    <div class="result-title">${escapeHtml(item.name)}</div>
                    <div class="result-badges">
                        <span class="status-badge status-${item.status}">${item.status}</span>
                    </div>
                </div>
                ${item.description ? `<div class="result-description">${escapeHtml(item.description)}</div>` : ''}
                <div class="result-meta">
                    ${item.due_date ? `Due: ${formatDate(item.due_date)} • ` : ''}
                    ID: ${item.id.substring(0, 8)}
                </div>
            `;
        }
        
        resultItem.innerHTML = content;
        list.appendChild(resultItem);
    });
    
    section.appendChild(list);
    return section;
}

function handleSearchResultClick(item, type) {
    // Close search modal
    hideModal('search-results-modal');
    
    // Navigate to appropriate page and show item
    if (type === 'task') {
        showPage('tasks');
        // Optionally highlight the specific task
    } else if (type === 'note') {
        showPage('notes');
        // Optionally open the note for editing
    } else if (type === 'package') {
        showPage('projects');
        // Optionally filter by this project
    }
}

// Theme functionality
function toggleTheme() {
    const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.body.className = newTheme + '-theme';
    localStorage.setItem('theme', newTheme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const themeBtn = document.querySelector('.theme-toggle');
    const isDark = document.body.classList.contains('dark-theme');
    themeBtn.textContent = isDark ? '☀️' : '🌙';
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatDueDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const today = new Date();
    const diffTime = date.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    if (diffDays === -1) return 'Due yesterday';
    if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`;
    if (diffDays <= 7) return `Due in ${diffDays} days`;
    
    return `Due ${formatDate(dateString)}`;
}

function calculateProjectProgress(project) {
    // This would calculate actual progress based on completed tasks
    // For now, return a placeholder
    return Math.floor(Math.random() * 100);
}

function getProjectName(projectId) {
    const project = projects.find(p => p.id === projectId);
    return project ? project.name : 'Unknown Project';
}

function updateProjectSelectors() {
    const selectors = document.querySelectorAll('#task-project, #note-project');
    selectors.forEach(selector => {
        const currentValue = selector.value;
        selector.innerHTML = '<option value="">No Project</option>' +
            projects.map(project => 
                `<option value="${project.id}" ${project.id === currentValue ? 'selected' : ''}>${escapeHtml(project.name)}</option>`
            ).join('');
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Notification functions
function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 16px',
        borderRadius: '6px',
        color: 'white',
        fontWeight: '500',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease-out'
    });
    
    if (type === 'success') {
        notification.style.background = 'var(--success-green)';
    } else if (type === 'error') {
        notification.style.background = 'var(--danger-red)';
    } else {
        notification.style.background = 'var(--primary-blue)';
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Keyboard shortcut handlers
function handleSaveShortcut() {
    const activeModal = document.querySelector('.modal-overlay.active');
    if (activeModal) {
        handleModalSubmit(activeModal);
    }
}

function handleSaveAndNewShortcut() {
    const activeModal = document.querySelector('.modal-overlay.active');
    if (activeModal) {
        // Save current and prepare for new
        handleModalSubmit(activeModal, true);
    }
}

function handleModalSubmit(modal, saveAndNew = false) {
    const modalId = modal.id;
    
    switch (modalId) {
        case 'task-modal':
            createTask(saveAndNew);
            break;
        case 'note-modal':
            createNote(saveAndNew);
            break;
        case 'project-modal':
            createProject(saveAndNew);
            break;
        default:
            console.log('Unknown modal:', modalId);
    }
}

// Edit and delete functionality
async function editTask(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) {
        showError('Task not found');
        return;
    }
    
    // Populate edit form
    document.getElementById('task-title').value = task.title;
    document.getElementById('task-description').value = task.description || '';
    document.getElementById('task-due-date').value = task.due_date ? task.due_date.split('T')[0] : '';
    document.getElementById('task-project').value = task.package_id || '';
    document.getElementById('task-tags').value = task.tags ? task.tags.join(', ') : '';
    
    // Set priority
    document.querySelectorAll('.priority-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.priority-btn[data-priority="${task.priority}"]`).classList.add('active');
    
    // Change modal title and button
    document.querySelector('#task-modal .modal-header h3').textContent = 'Edit Task';
    document.querySelector('#task-modal .primary-btn').textContent = 'Update Task';
    document.querySelector('#task-modal .primary-btn').onclick = () => updateTask(taskId);
    
    showModal('task-modal');
}

async function updateTask(taskId) {
    const title = document.getElementById('task-title').value.trim();
    if (!title) {
        showError('Task title is required');
        return;
    }
    
    const priority = document.querySelector('.priority-btn.active')?.getAttribute('data-priority') || 'medium';
    const dueDate = document.getElementById('task-due-date').value;
    const projectId = document.getElementById('task-project').value;
    const description = document.getElementById('task-description').value.trim();
    const tags = document.getElementById('task-tags').value.split(',').map(tag => tag.trim()).filter(Boolean);
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                description: description || null,
                priority,
                due_date: dueDate || null,
                package_id: projectId || null,
                tags
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update task');
        }
        
        hideModal('task-modal');
        showSuccess('Task updated successfully');
        
        // Reset modal for next use
        resetTaskModal();
        
        // Reload data
        await Promise.all([loadStats(), loadTasks()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showError('Failed to update task');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete task');
        }
        
        showSuccess('Task deleted successfully');
        
        // Reload data
        await Promise.all([loadStats(), loadTasks()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showError('Failed to delete task');
    }
}

async function editNote(noteId) {
    const note = notes.find(n => n.id === noteId);
    if (!note) {
        showError('Note not found');
        return;
    }
    
    // Populate edit form
    document.getElementById('note-title').value = note.title;
    document.getElementById('note-content').value = note.content || '';
    document.getElementById('note-project').value = note.package_id || '';
    document.getElementById('note-tags').value = note.tags ? note.tags.join(', ') : '';
    
    // Change modal title and button
    document.querySelector('#note-modal .modal-header h3').textContent = 'Edit Note';
    document.querySelector('#note-modal .primary-btn').textContent = 'Update Note';
    document.querySelector('#note-modal .primary-btn').onclick = () => updateNote(noteId);
    
    showModal('note-modal');
}

async function updateNote(noteId) {
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    
    if (!title) {
        showError('Note title is required');
        return;
    }
    
    const projectId = document.getElementById('note-project').value;
    const tags = document.getElementById('note-tags').value.split(',').map(tag => tag.trim()).filter(Boolean);
    
    try {
        const response = await fetch(`/api/notes/${noteId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                content: content || '',
                package_id: projectId || null,
                tags
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update note');
        }
        
        hideModal('note-modal');
        showSuccess('Note updated successfully');
        
        // Reset modal for next use
        resetNoteModal();
        
        // Reload data
        await Promise.all([loadStats(), loadNotes()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error updating note:', error);
        showError('Failed to update note');
    }
}

async function deleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/notes/${noteId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete note');
        }
        
        showSuccess('Note deleted successfully');
        
        // Reload data
        await Promise.all([loadStats(), loadNotes()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error deleting note:', error);
        showError('Failed to delete note');
    }
}

function openNote(noteId) {
    editNote(noteId);
}

async function editProject(projectId) {
    const project = projects.find(p => p.id === projectId);
    if (!project) {
        showError('Project not found');
        return;
    }
    
    // Populate edit form
    document.getElementById('project-name').value = project.name;
    document.getElementById('project-description').value = project.description || '';
    document.getElementById('project-due-date').value = project.due_date ? project.due_date.split('T')[0] : '';
    
    // Change modal title and button
    document.querySelector('#project-modal .modal-header h3').textContent = 'Edit Project';
    document.querySelector('#project-modal .primary-btn').textContent = 'Update Project';
    document.querySelector('#project-modal .primary-btn').onclick = () => updateProject(projectId);
    
    showModal('project-modal');
}

async function updateProject(projectId) {
    const name = document.getElementById('project-name').value.trim();
    
    if (!name) {
        showError('Project name is required');
        return;
    }
    
    const description = document.getElementById('project-description').value.trim();
    const dueDate = document.getElementById('project-due-date').value;
    
    try {
        const response = await fetch(`/api/packages/${projectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                description: description || null,
                due_date: dueDate || null
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update project');
        }
        
        hideModal('project-modal');
        showSuccess('Project updated successfully');
        
        // Reset modal for next use
        resetProjectModal();
        
        // Reload data
        await Promise.all([loadStats(), loadProjects()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error updating project:', error);
        showError('Failed to update project');
    }
}

async function deleteProject(projectId) {
    if (!confirm('Are you sure you want to delete this project? This will also delete all associated tasks and notes.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/packages/${projectId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete project');
        }
        
        showSuccess('Project deleted successfully');
        
        // Reload data
        await Promise.all([loadStats(), loadProjects()]);
        if (currentPage === 'dashboard') {
            await loadDashboardData();
        }
    } catch (error) {
        console.error('Error deleting project:', error);
        showError('Failed to delete project');
    }
}

function viewProject(projectId) {
    // For now, just switch to tasks view with project filter
    showPage('tasks');
    // TODO: Implement project-specific task filtering
}

// Form clearing functions
function clearTaskForm() {
    document.getElementById('task-title').value = '';
    document.getElementById('task-due-date').value = '';
    document.getElementById('task-project').value = '';
    document.getElementById('task-description').value = '';
    document.getElementById('task-tags').value = '';
    
    // Reset priority to medium
    document.querySelectorAll('.priority-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.priority-btn[data-priority="medium"]').classList.add('active');
    
    // Focus title input
    setTimeout(() => document.getElementById('task-title').focus(), 100);
}

function clearNoteForm() {
    document.getElementById('note-title').value = '';
    document.getElementById('note-content').value = '';
    document.getElementById('note-project').value = '';
    document.getElementById('note-tags').value = '';
    
    // Focus title input
    setTimeout(() => document.getElementById('note-title').focus(), 100);
}

function clearProjectForm() {
    document.getElementById('project-name').value = '';
    document.getElementById('project-description').value = '';
    document.getElementById('project-due-date').value = '';
    
    // Focus name input
    setTimeout(() => document.getElementById('project-name').focus(), 100);
}

// Reset modal functions
function resetTaskModal() {
    document.querySelector('#task-modal .modal-header h3').textContent = 'Create New Task';
    document.querySelector('#task-modal .primary-btn').textContent = 'Create Task';
    document.querySelector('#task-modal .primary-btn').onclick = () => createTask();
}

function resetNoteModal() {
    document.querySelector('#note-modal .modal-header h3').textContent = 'Create New Note';
    document.querySelector('#note-modal .primary-btn').textContent = 'Create Note';
    document.querySelector('#note-modal .primary-btn').onclick = () => createNote();
}

function resetProjectModal() {
    document.querySelector('#project-modal .modal-header h3').textContent = 'Create New Project';
    document.querySelector('#project-modal .primary-btn').textContent = 'Create Project';
    document.querySelector('#project-modal .primary-btn').onclick = () => createProject();
}

// Update keyboard shortcut display based on platform
function updateKeyboardShortcutDisplay() {
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const modifier = isMac ? 'Cmd' : 'Ctrl';
    
    // Update search shortcut
    const searchShortcut = document.getElementById('search-shortcut');
    if (searchShortcut) {
        searchShortcut.textContent = `${modifier}+K`;
    }
    
    // Update modal shortcuts
    document.querySelectorAll('.modal-shortcuts kbd').forEach(kbd => {
        const text = kbd.textContent;
        if (text.includes('Ctrl')) {
            kbd.textContent = text.replace('Ctrl', modifier);
        }
    });
}