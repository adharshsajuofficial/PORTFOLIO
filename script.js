document.addEventListener('DOMContentLoaded', () => {
    const projectContainer = document.getElementById('projects-container');
    const projectCountEl = document.getElementById('project-count');
    const filterButtons = document.querySelectorAll('.filter-btn');
    let activeFilter = 'all';

    // 1. Fetch dynamically generated project data from JSON
    fetch('projects.json')
        .then(response => {
            if (!response.ok) throw new Error('No projects.json found yet. Run python script.');
            return response.json();
        })
        .then(projects => {
            renderProjects(projects);
            setupFilterControls();
        })
        .catch(err => {
            console.error('Error loading projects:', err);
            projectContainer.innerHTML = `<p style="color: var(--text-secondary);">Failed to load dynamic projects. Run automation script.</p>`;
        });

    // 2. Render dynamic HTML structures
    function renderProjects(projects) {
        projectContainer.innerHTML = '';
        let visibleCount = 0;

        projects.forEach(project => {
            const matchesFilter = activeFilter === 'all' || project.category === activeFilter;
            
            // Create Card Element
            const card = document.createElement('div');
            card.className = `project-card ${matchesFilter ? '' : 'hidden'}`;
            card.setAttribute('data-category', project.category);

            if (matchesFilter) visibleCount++;

            card.innerHTML = `
                <div class="project-img-placeholder">${project.language || 'Code'}</div>
                <div class="project-info">
                    <h3>${project.name}</h3>
                    <p>${project.description || 'No description provided. Click below to view the source repository codebase.'}</p>
                    <a href="${project.html_url}" target="_blank" class="project-link">View Repository →</a>
                </div>
            `;
            projectContainer.appendChild(card);
        });

        projectCountEl.textContent = visibleCount;
    }

    // 3. Setup Interactive Filtering Logic
    function setupFilterControls() {
        filterButtons.forEach(button => {
            // Remove any cloning or double listeners by replacing element behavior
            button.onclick = (e) => {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                e.currentTarget.classList.add('active');
                
                activeFilter = e.currentTarget.getAttribute('data-filter');
                
                // Re-fetch local cache or re-trigger visibility calculations
                fetch('projects.json')
                    .then(res => res.json())
                    .then(projects => renderProjects(projects));
            };
        });
    }
});