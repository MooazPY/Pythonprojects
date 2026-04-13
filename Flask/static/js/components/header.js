/**
 * Header Component
 * Generates the header HTML with navigation and auth state
 * Professional Design Enhancement
 */

let isHeaderInitialized = false;
let sessionStatePromise = null;
let sessionStateTimestamp = 0;
const SESSION_CACHE_MS = 30000;

function getSessionFallback() {
  return {
    logged_in: localStorage.getItem('isLoggedIn') === 'true',
    is_admin: localStorage.getItem('isAdmin') === 'true',
    user_email: localStorage.getItem('userEmail') || '',
    user_name: localStorage.getItem('userName') || '',
    patient_id: localStorage.getItem('patientId') || '',
    age: localStorage.getItem('age') || '',
    gender: localStorage.getItem('gender') || ''
  };
}

function syncSessionStorage(session) {
  localStorage.setItem('isLoggedIn', session.logged_in ? 'true' : 'false');
  localStorage.setItem('isAdmin', session.is_admin ? 'true' : 'false');

  if (session.user_email) localStorage.setItem('userEmail', session.user_email);
  if (session.user_name) localStorage.setItem('userName', session.user_name);
  if (session.patient_id) localStorage.setItem('patientId', session.patient_id);
  if (session.age !== undefined && session.age !== null && session.age !== '') localStorage.setItem('age', session.age);
  if (session.gender) localStorage.setItem('gender', session.gender);
}

function invalidateSessionState() {
  sessionStatePromise = null;
  sessionStateTimestamp = 0;
}

function getSessionState(forceRefresh = false) {
  const now = Date.now();
  if (!forceRefresh && sessionStatePromise && (now - sessionStateTimestamp) < SESSION_CACHE_MS) {
    return sessionStatePromise;
  }

  sessionStateTimestamp = now;
  sessionStatePromise = fetch('/check-session')
    .then(res => res.json())
    .then(data => {
      syncSessionStorage(data);
      return data;
    })
    .catch(() => getSessionFallback());

  return sessionStatePromise;
}

window.getSessionState = getSessionState;
window.invalidateSessionState = invalidateSessionState;

function generateHeader() {
  return `
<header id="site-header">
  <div class="top-bar">
    <div class="container">
      <div class="row">
        <div class="col-md-6 col-sm-7 col-xs-12">
          <span style="color:rgba(255,255,255,0.85);font-size:13px;font-weight:500;">
            <img src="/static/images/flag-egypt.png" style="width:20px;vertical-align:middle;margin-right:6px;border-radius:2px;"> Egypt &nbsp;|&nbsp;
            <i class="fa fa-phone" style="margin-right:5px;color:rgba(255,255,255,0.7);"></i>+20 2 1234 5678
          </span>
        </div>
        <div class="col-md-6 col-sm-5 col-xs-12 text-right">
          <span style="color:rgba(255,255,255,0.7);font-size:13px;">
            <i class="fa fa-envelope" style="margin-right:5px;"></i>info@livercare.com
          </span>
        </div>
      </div>
    </div>
  </div>

  <nav class="navbar navbar-default">
    <div class="container">
      <div class="navbar-header">
        <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#navbar-collapse">
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>
        <a class="navbar-brand" href="index.html">
          <img src="/static/images/logo.png" alt="Liver Care">
        </a>
      </div>

      <div class="collapse navbar-collapse" id="navbar-collapse">
        <ul class="nav navbar-nav navbar-right" id="nav-menu">
          <li id="nav-home"><a href="index.html">Home</a></li>
          <li id="nav-news"><a href="news.html">News</a></li>
          <li id="nav-contact"><a href="contact-us.html">Contact Us</a></li>
          <li id="nav-faq"><a href="faq.html">Help</a></li>
          <!-- Menu items will be dynamically inserted here by checkLoginStatus() -->
        </ul>
      </div>
    </div>
  </nav>
</header>
  `;
}

function setActiveNavItem() {
  const path = window.location.pathname;
  const filename = path.split('/').pop() || 'index.html';

  document.querySelectorAll('#nav-menu li').forEach(item => item.classList.remove('active'));

  const navMap = {
    'index.html': 'nav-home',
    '': 'nav-home',
    'news.html': 'nav-news',
    'contact-us.html': 'nav-contact',
    'faq.html': 'nav-faq',
    'admin-dashboard.html': 'navDashboard',
  };

  const activeId = navMap[filename];
  if (activeId) {
    const el = document.getElementById(activeId);
    if (el) el.classList.add('active');
  }
}

function renderHeader() {
  const headerContainer = document.getElementById('header-container');
  if (!headerContainer) return;
  
  // Only render header once
  if (isHeaderInitialized) {
    console.log('Header already rendered, only updating menu...');
    checkLoginStatus(); // Just update the menu, don't re-render
    return;
  }
  
  headerContainer.innerHTML = generateHeader();
  setActiveNavItem();
  initStickyHeader();
  checkLoginStatus();
  isHeaderInitialized = true;
}

function initStickyHeader() {
  const header = document.getElementById('site-header');
  if (!header) return;
  
  // Remove existing listener to prevent duplicates
  window.removeEventListener('scroll', stickyScrollHandler);
  window.addEventListener('scroll', stickyScrollHandler);
  
  function stickyScrollHandler() {
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }
}

// Show admin profile alert notification
function showAdminAccessAlert(message, title = 'Access Denied') {
  showNotification(message, 'error', title);
}

function updateBaseNavForRole(isAdmin) {
  const baseNavIds = ['nav-home', 'nav-news', 'nav-contact', 'nav-faq'];
  baseNavIds.forEach(itemId => {
    const element = document.getElementById(itemId);
    if (element) {
      element.style.display = isAdmin ? 'none' : '';
    }
  });

  const brandLink = document.querySelector('.navbar-brand');
  if (brandLink) {
    brandLink.setAttribute('href', isAdmin ? '/admin-dashboard.html' : 'index.html');
  }
}

function handleAdminAccessMessage() {
  const params = new URLSearchParams(window.location.search);
  const deniedTarget = params.get('denied');
  if (!deniedTarget) return;

  const messages = {
    profile: 'Admin accounts do not have access to the patient profile page.',
    results: 'Admin accounts do not have access to patient results pages.'
  };

  const message = messages[deniedTarget] || 'You do not have access to this page.';
  showAdminAccessAlert(message);

  params.delete('denied');
  const cleanUrl = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ''}${window.location.hash}`;
  window.history.replaceState({}, '', cleanUrl);
}

function checkLoginStatus() {
  getSessionState()
    .then(data => {
      updateNavMenu(data.logged_in || false, data.is_admin || false);
    });
}

// Updated function to update navigation menu - CLEARS existing items first
function updateNavMenu(isLoggedIn, isAdmin = false) {
  const navMenu = document.getElementById('nav-menu');
  if (!navMenu) return;

  updateBaseNavForRole(isAdmin);

  // Remove ALL existing auth menu items (clean slate)
  const authItems = ['navLogin', 'navRegister', 'navProfile', 'navLogout', 'navDashboard', 'navResults'];
  authItems.forEach(itemId => {
    const element = document.getElementById(itemId);
    if (element) element.remove();
  });

  if (isLoggedIn) {
    if (isAdmin) {
      // ADMIN MENU
      const dashboardLi = document.createElement('li');
      dashboardLi.id = 'navDashboard';
      dashboardLi.innerHTML = `<a href="/admin-dashboard.html"><i class="fa fa-dashboard"></i> Dashboard</a>`;
      
      const logoutLi = document.createElement('li');
      logoutLi.id = 'navLogout';
      logoutLi.innerHTML = `<a href="#" onclick="handleLogout(event)"><i class="fa fa-sign-out"></i> Logout</a>`;
      
      navMenu.appendChild(dashboardLi);
      navMenu.appendChild(logoutLi);
    } else {
      // REGULAR USER MENU
      const profileLi = document.createElement('li');
      profileLi.id = 'navProfile';
      profileLi.innerHTML = `<a href="/profile.html"><i class="fa fa-user-circle"></i> Profile</a>`;
      
      const resultsLi = document.createElement('li');
      resultsLi.id = 'navResults';
      resultsLi.innerHTML = `<a href="/my-results.html"><i class="fa fa-history"></i> My Results</a>`;
      
      const logoutLi = document.createElement('li');
      logoutLi.id = 'navLogout';
      logoutLi.innerHTML = `<a href="#" onclick="handleLogout(event)"><i class="fa fa-sign-out"></i> Logout</a>`;
      
      navMenu.appendChild(profileLi);
      navMenu.appendChild(resultsLi);
      navMenu.appendChild(logoutLi);
    }
    
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('isAdmin', isAdmin ? 'true' : 'false');
  } else {
    // Not logged in - show Login and Register
    const loginLi = document.createElement('li');
    loginLi.id = 'navLogin';
    loginLi.innerHTML = `<a href="/login.html">Login</a>`;
    
    const registerLi = document.createElement('li');
    registerLi.id = 'navRegister';
    registerLi.innerHTML = `<a href="/register.html" class="register-btn">Register</a>`;
    
    navMenu.appendChild(loginLi);
    navMenu.appendChild(registerLi);
    
    localStorage.setItem('isLoggedIn', 'false');
    localStorage.setItem('isAdmin', 'false');
  }

  setActiveNavItem();
}

// NOTIFICATION SYSTEM
function showNotification(message, type = 'success', title = null) {
    const existing = document.querySelector('.notification-message');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = `notification-message ${type}`;
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; color: white;
        padding: 16px 24px; border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2); z-index: 10000;
        font-family: 'Poppins', sans-serif; display: flex;
        align-items: center; gap: 12px; animation: slideIn 0.4s ease;
        max-width: 380px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#0ea5e9'};
    `;
    
    notification.innerHTML = `
        <div style="flex:1;">
            <strong style="display:block; font-size: 15px;">${title || (type === 'error' ? 'Error' : type === 'success' ? 'Success' : 'Notice')}</strong>
            <p style="margin:0; font-size:13px; opacity:0.9;">${message}</p>
        </div>
        <button onclick="this.parentElement.remove()" style="background:none; border:none; color:white; cursor:pointer; font-size: 20px;">&times;</button>
    `;
    
    if (!document.querySelector('#notification-keyframes')) {
        const style = document.createElement('style');
        style.id = 'notification-keyframes';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes fadeOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    setTimeout(() => { if(notification.parentElement) notification.remove(); }, 5000);
}

// Main logout function
function handleLogout(event) {
  if (event) {
    event.preventDefault();
  }
  
  console.log('Logging out...');
  
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.style.display = 'flex';
  
  invalidateSessionState();
  localStorage.clear();
  
  fetch('/logout', { 
    method: 'GET',
    credentials: 'same-origin'
  })
  .then(() => {
    showNotification('Logged out successfully!', 'info', 'Goodbye');
    updateNavMenu(false, false);
    if (overlay) overlay.style.display = 'none';
    setTimeout(() => {
      window.location.href = '/index.html';
    }, 1500);
  })
  .catch(() => {
    showNotification('Logged out successfully!', 'info', 'Goodbye');
    updateNavMenu(false, false);
    if (overlay) overlay.style.display = 'none';
    setTimeout(() => {
      window.location.href = '/index.html';
    }, 1500);
  });
}

function logout() {
  handleLogout();
}

document.addEventListener('visibilitychange', function() {
  if (!document.hidden) {
    checkLoginStatus();
  }
});

// Make sure DOM is fully loaded before rendering
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function () {
    renderHeader();
    handleAdminAccessMessage();
  });
} else {
  renderHeader();
  handleAdminAccessMessage();
}
