// Lament Registry - Client-side JavaScript

// API Key Management
const API_KEY_STORAGE = 'lament_api_key';

function getApiKey() {
    return localStorage.getItem(API_KEY_STORAGE);
}

function setApiKey(key) {
    localStorage.setItem(API_KEY_STORAGE, key);
}

function clearApiKey() {
    localStorage.removeItem(API_KEY_STORAGE);
}

// API Client
class RegistryAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || window.location.origin;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const apiKey = getApiKey();

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (apiKey) {
            headers['Authorization'] = `Bearer ${apiKey}`;
        }

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.statusText}`);
        }

        return response.json();
    }

    async searchPackages(query) {
        return this.request(`/api/search?q=${encodeURIComponent(query)}`);
    }

    async getPackage(name) {
        return this.request(`/api/packages/${name}`);
    }

    async getPackageVersion(name, version) {
        return this.request(`/api/packages/${name}/${version}`);
    }

    async publishPackage(formData) {
        const apiKey = getApiKey();
        const response = await fetch(`${this.baseUrl}/api/packages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Publish failed: ${response.statusText}`);
        }

        return response.json();
    }

    async unpublishPackage(name, version) {
        return this.request(`/api/packages/${name}/${version}`, {
            method: 'DELETE'
        });
    }

    async login(username, password) {
        return this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    }

    async register(username, email, password) {
        return this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    }

    async getStats() {
        return this.request('/api/stats');
    }
}

// Initialize API client
const api = new RegistryAPI();

// Search functionality
function initSearch() {
    const searchForm = document.querySelector('.search-box form');
    const searchInput = document.querySelector('.search-input');

    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = searchInput.value.trim();

            if (query) {
                try {
                    const results = await api.searchPackages(query);
                    displaySearchResults(results);
                } catch (error) {
                    console.error('Search failed:', error);
                }
            }
        });
    }

    // Autocomplete
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();

            if (query.length >= 2) {
                debounceTimer = setTimeout(async () => {
                    try {
                        const results = await api.searchPackages(query);
                        showAutocomplete(results.slice(0, 5));
                    } catch (error) {
                        console.error('Autocomplete failed:', error);
                    }
                }, 300);
            }
        });
    }
}

function displaySearchResults(results) {
    // This would update the page with search results
    // For now, just redirect to browse page with query
    const query = document.querySelector('.search-input').value;
    window.location.href = `/browse?q=${encodeURIComponent(query)}`;
}

function showAutocomplete(suggestions) {
    // TODO: Implement autocomplete dropdown
    console.log('Suggestions:', suggestions);
}

// Authentication
function initAuth() {
    const loginForm = document.querySelector('.login-form');
    const registerForm = document.querySelector('.register-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.querySelector('#username').value;
            const password = document.querySelector('#password').value;

            try {
                const response = await api.login(username, password);
                setApiKey(response.access_token);
                window.location.href = '/dashboard';
            } catch (error) {
                alert('Login failed: ' + error.message);
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.querySelector('#username').value;
            const email = document.querySelector('#email').value;
            const password = document.querySelector('#password').value;

            try {
                const response = await api.register(username, email, password);
                setApiKey(response.access_token);
                window.location.href = '/dashboard';
            } catch (error) {
                alert('Registration failed: ' + error.message);
            }
        });
    }
}

// Package actions
function unpublishPackage(name, version) {
    if (confirm(`Are you sure you want to unpublish ${name}@${version}?`)) {
        api.unpublishPackage(name, version)
            .then(() => {
                alert('Package unpublished successfully');
                location.reload();
            })
            .catch(error => {
                alert('Failed to unpublish package: ' + error.message);
            });
    }
}

function generateApiKey() {
    api.request('/api/auth/generate-key', { method: 'POST' })
        .then(response => {
            alert(`New API key generated:\n\n${response.api_key}\n\nSave this key securely!`);
            location.reload();
        })
        .catch(error => {
            alert('Failed to generate API key: ' + error.message);
        });
}

// Admin actions
function makeAdmin(userId) {
    if (confirm('Make this user an admin?')) {
        api.request(`/api/admin/users/${userId}/make-admin`, { method: 'POST' })
            .then(() => {
                alert('User is now an admin');
                location.reload();
            })
            .catch(error => {
                alert('Failed to make user admin: ' + error.message);
            });
    }
}

function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        api.request(`/api/admin/users/${userId}`, { method: 'DELETE' })
            .then(() => {
                alert('User deleted');
                location.reload();
            })
            .catch(error => {
                alert('Failed to delete user: ' + error.message);
            });
    }
}

// Statistics update
function updateStats() {
    api.getStats()
        .then(stats => {
            document.querySelectorAll('.stat-number').forEach((el, index) => {
                const values = [
                    stats.total_packages,
                    stats.total_versions,
                    stats.total_downloads,
                    stats.total_users
                ];
                if (values[index] !== undefined) {
                    animateNumber(el, values[index]);
                }
            });
        })
        .catch(error => {
            console.error('Failed to update stats:', error);
        });
}

function animateNumber(element, target) {
    const duration = 1000;
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

// Clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            // Show tooltip or notification
            showNotification('Copied to clipboard');
        })
        .catch(error => {
            console.error('Failed to copy:', error);
        });
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initSearch();
    initAuth();

    // Update stats if on homepage
    if (document.querySelector('.stats-section')) {
        updateStats();
    }

    // Add copy buttons to code blocks
    document.querySelectorAll('pre code').forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Copy';
        button.onclick = () => copyToClipboard(block.textContent);

        block.parentElement.style.position = 'relative';
        block.parentElement.appendChild(button);
    });
});

// Export for use in inline scripts
window.RegistryAPI = RegistryAPI;
window.api = api;
window.unpublishPackage = unpublishPackage;
window.generateApiKey = generateApiKey;
window.makeAdmin = makeAdmin;
window.deleteUser = deleteUser;
