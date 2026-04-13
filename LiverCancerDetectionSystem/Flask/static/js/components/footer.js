/**
 * Footer Component
 * Generates the footer HTML - Professional Design
 */

function generateFooter() {
  const year = new Date().getFullYear();
  return `
<div class="footer-bar">
  <div class="container">
    <div class="row">
      <div class="col-xs-12 text-center">
        <p style="color:rgba(255,255,255,0.7);font-size:14px;margin-bottom:16px;">
          <i class="fa fa-phone" style="margin-right:8px;color:#0ea5e9;"></i>
          Emergency Hotline: <strong style="color:#fff;">123</strong>
          &nbsp;&nbsp;|&nbsp;&nbsp;
          <i class="fa fa-envelope" style="margin-right:8px;color:#0ea5e9;"></i>
          <strong style="color:#fff;">info@livercare.com</strong>
        </p>
        <div class="social-links" style="display:flex;justify-content:center;gap:12px;">
          <a href="#" title="Facebook" style="width:42px;height:42px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;text-decoration:none;transition:all 0.3s;">
            <i class="fa fa-facebook"></i>
          </a>
          <a href="#" title="X / Twitter" style="width:42px;height:42px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:14px;font-weight:700;text-decoration:none;transition:all 0.3s;">
            X
          </a>
          <a href="#" title="LinkedIn" style="width:42px;height:42px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:17px;text-decoration:none;transition:all 0.3s;">
            <i class="fa fa-linkedin"></i>
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<footer>
  <div class="container">
    <div class="row" style="padding-bottom:40px;">

      <!-- About -->
      <div class="col-md-4 col-sm-6 col-xs-12" style="margin-bottom:40px;">
        <img src="/static/images/logo-white.png" style="width:140px;margin-bottom:20px;display:block;" alt="Liver Care">
        <p style="color:rgba(255,255,255,0.55);font-size:14px;line-height:1.85;margin-bottom:20px;">
          Liver Care is an AI-powered platform for early liver cancer detection. We help patients get fast, accurate CT scan analysis from the comfort of their homes.
        </p>
      </div>

      <!-- Navigation -->
      <div class="col-md-2 col-sm-6 col-xs-12" style="margin-bottom:40px;">
        <h4 style="color:#fff;font-size:18px;font-weight:700;margin-bottom:20px;letter-spacing:-0.3px;">Navigation</h4>
        <ul style="list-style:none;padding:0;margin:0;">
          <li style="margin-bottom:12px;">
            <a id="footerHomeLink" href="index.html" style="color:rgba(255,255,255,0.55);font-size:14px;text-decoration:none;display:flex;align-items:center;gap:8px;transition:all 0.2s ease;">
              <span style="color:#0ea5e9;font-size:18px;transition:transform 0.2s ease;display:inline-block;">›</span>
              <span id="footerHomeText" style="transition:color 0.2s ease;">Home</span>
            </a>
          </li>
          <li style="margin-bottom:12px;">
            <a href="news.html" style="color:rgba(255,255,255,0.55);font-size:14px;text-decoration:none;display:flex;align-items:center;gap:8px;transition:all 0.2s ease;">
              <span style="color:#0ea5e9;font-size:18px;transition:transform 0.2s ease;display:inline-block;">›</span>
              <span style="transition:color 0.2s ease;">News</span>
            </a>
          </li>
          <li style="margin-bottom:12px;">
            <a href="contact-us.html" style="color:rgba(255,255,255,0.55);font-size:14px;text-decoration:none;display:flex;align-items:center;gap:8px;transition:all 0.2s ease;">
              <span style="color:#0ea5e9;font-size:18px;transition:transform 0.2s ease;display:inline-block;">›</span>
              <span style="transition:color 0.2s ease;">Contact Us</span>
            </a>
          </li>
          <li style="margin-bottom:12px;">
            <a href="faq.html" style="color:rgba(255,255,255,0.55);font-size:14px;text-decoration:none;display:flex;align-items:center;gap:8px;transition:all 0.2s ease;">
              <span style="color:#0ea5e9;font-size:18px;transition:transform 0.2s ease;display:inline-block;">›</span>
              <span style="transition:color 0.2s ease;">Help &amp; FAQ</span>
            </a>
          </li>
          <li id="footerLoginItem" style="margin-bottom:12px;">
            <a id="footerLoginLink" href="#" onclick="handleFooterLogin(event); return false;" style="color:rgba(255,255,255,0.55);font-size:14px;text-decoration:none;display:flex;align-items:center;gap:8px;transition:all 0.2s ease;">
              <span style="color:#0ea5e9;font-size:18px;transition:transform 0.2s ease;display:inline-block;">›</span>
              <span style="transition:color 0.2s ease;">Login</span>
            </a>
          </li>
          <li id="footerRegisterItem" style="margin-bottom:12px;">
            <a id="footerRegisterLink" href="#" onclick="handleFooterRegister(event); return false;" style="color:rgba(255,255,255,0.55);font-size:14px;text-decoration:none;display:flex;align-items:center;gap:8px;transition:all 0.2s ease;">
              <span style="color:#0ea5e9;font-size:18px;transition:transform 0.2s ease;display:inline-block;">›</span>
              <span style="transition:color 0.2s ease;">Register</span>
            </a>
          </li>
        </ul>
      </div>

      <!-- Services -->
      <div class="col-md-2 col-sm-6 col-xs-12" style="margin-bottom:40px;">
        <h4 style="color:#fff;font-size:18px;font-weight:700;margin-bottom:20px;letter-spacing:-0.3px;">Services</h4>
        <ul style="list-style:none;padding:0;margin:0;">
          <li style="margin-bottom:12px;">
            <a id="footerServiceLink" href="index.html" style="color:rgba(255,255,255,0.55);font-size:14px;text-decoration:none;display:flex;align-items:center;gap:8px;transition:all 0.2s ease;">
              <span style="color:#0ea5e9;font-size:18px;transition:transform 0.2s ease;display:inline-block;">›</span>
              <span id="footerServiceText" style="transition:color 0.2s ease;">CT Scan Analysis</span>
            </a>
          </li>
          <li style="margin-bottom:12px;">
            <a href="contact-us.html" style="color:rgba(255,255,255,0.55);font-size:14px;text-decoration:none;display:flex;align-items:center;gap:8px;transition:all 0.2s ease;">
              <span style="color:#0ea5e9;font-size:18px;transition:transform 0.2s ease;display:inline-block;">›</span>
              <span style="transition:color 0.2s ease;">Patient Support</span>
            </a>
          </li>
        </ul>
      </div>

      <!-- Contact Info -->
      <div class="col-md-4 col-sm-6 col-xs-12" style="margin-bottom:40px;">
        <h4 style="color:#fff;font-size:18px;font-weight:700;margin-bottom:20px;letter-spacing:-0.3px;">Contact Info</h4>
        <div style="margin-bottom:18px;display:flex;gap:14px;align-items:flex-start;">
          <div style="width:40px;height:40px;min-width:40px;background:rgba(14,165,233,0.12);border-radius:10px;display:flex;align-items:center;justify-content:center;">
            <i class="fa fa-phone" style="color:#0ea5e9;font-size:16px;"></i>
          </div>
          <div>
            <p style="color:rgba(255,255,255,0.85);font-size:14px;margin:0 0 2px;font-weight:600;">Phone</p>
            <p style="color:rgba(255,255,255,0.5);font-size:13px;margin:0;line-height:1.6;">+20 2 1234 5678<br>Emergency: 123</p>
          </div>
        </div>
        <div style="display:flex;gap:14px;align-items:flex-start;">
          <div style="width:40px;height:40px;min-width:40px;background:rgba(14,165,233,0.12);border-radius:10px;display:flex;align-items:center;justify-content:center;">
            <i class="fa fa-envelope" style="color:#0ea5e9;font-size:16px;"></i>
          </div>
          <div>
            <p style="color:rgba(255,255,255,0.85);font-size:14px;margin:0 0 2px;font-weight:600;">Email</p>
            <p style="color:rgba(255,255,255,0.5);font-size:13px;margin:0;line-height:1.6;">info@livercare.com<br>support@livercare.com</p>
          </div>
        </div>
      </div>

    </div>

    <!-- Copyright Bar -->
    <div style="border-top:1px solid rgba(255,255,255,0.07);padding-top:24px;text-align:center;">
      <p style="color:rgba(255,255,255,0.35);font-size:13px;margin:0;">
        &copy; ${year} <strong style="color:rgba(255,255,255,0.55);">Liver Care</strong>. All rights reserved.
        &nbsp;|&nbsp;
        <a href="#" style="color:#0ea5e9;text-decoration:none;">Privacy Policy</a>
        &nbsp;|&nbsp;
        <a href="#" style="color:#0ea5e9;text-decoration:none;">Terms of Service</a>
      </p>
    </div>

  </div>
</footer>

<!-- Footer Hover Styles -->
<style>
  footer ul li a:hover {
    color: #ffffff !important;
  }
  
  footer ul li a:hover span:first-child {
    transform: translateX(5px);
    color: #38bdf8 !important;
  }
  
  footer ul li a span:first-child {
    font-size: 18px;
    color: #0ea5e9;
    transition: transform 0.2s ease;
    display: inline-block;
  }
  
  footer h4 {
    color: #fff;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 20px;
    letter-spacing: -0.3px;
    position: relative;
    padding-bottom: 10px;
  }
  
  footer h4::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 40px;
    height: 3px;
    background: #0ea5e9;
    border-radius: 2px;
  }
</style>
  `;
}

function renderFooter() {
  const footerContainer = document.getElementById('footer-container');
  if (footerContainer) {
    footerContainer.innerHTML = generateFooter();
    // Add hover effect to social links
    const socialLinks = footerContainer.querySelectorAll('.footer-bar a');
    socialLinks.forEach(link => {
      link.addEventListener('mouseenter', function() {
        this.style.background = '#0ea5e9';
        this.style.borderColor = '#0ea5e9';
        this.style.transform = 'translateY(-3px)';
        this.style.boxShadow = '0 6px 20px rgba(14,165,233,0.4)';
      });
      link.addEventListener('mouseleave', function() {
        this.style.background = 'rgba(255,255,255,0.1)';
        this.style.borderColor = 'rgba(255,255,255,0.15)';
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = 'none';
      });
    });

    syncFooterAccess();
  }
}

function updateFooterForRole(isLoggedIn, isAdmin) {
  const footerHomeLink = document.getElementById('footerHomeLink');
  const footerHomeText = document.getElementById('footerHomeText');
  const footerServiceLink = document.getElementById('footerServiceLink');
  const footerServiceText = document.getElementById('footerServiceText');
  const footerLoginItem = document.getElementById('footerLoginItem');
  const footerRegisterItem = document.getElementById('footerRegisterItem');

  if (isAdmin) {
    if (footerHomeLink) footerHomeLink.href = '/admin-dashboard.html';
    if (footerHomeText) footerHomeText.textContent = 'Dashboard';
    if (footerServiceLink) footerServiceLink.href = '/admin-dashboard.html';
    if (footerServiceText) footerServiceText.textContent = 'Admin Dashboard';
    if (footerLoginItem) footerLoginItem.style.display = 'none';
    if (footerRegisterItem) footerRegisterItem.style.display = 'none';
    return;
  }

  if (footerHomeLink) footerHomeLink.href = 'index.html';
  if (footerHomeText) footerHomeText.textContent = 'Home';
  if (footerServiceLink) footerServiceLink.href = 'index.html';
  if (footerServiceText) footerServiceText.textContent = 'CT Scan Analysis';
  if (footerLoginItem) footerLoginItem.style.display = isLoggedIn ? 'none' : '';
  if (footerRegisterItem) footerRegisterItem.style.display = isLoggedIn ? 'none' : '';
}

function syncFooterAccess() {
  const sessionLoader = window.getSessionState
    ? window.getSessionState()
    : fetch('/check-session').then(response => response.json());

  sessionLoader
    .then(data => {
      updateFooterForRole(data.logged_in === true, data.is_admin === true);
    })
    .catch(() => {
      const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
      const isAdmin = localStorage.getItem('isAdmin') === 'true';
      updateFooterForRole(isLoggedIn, isAdmin);
    });
}

/**
 * Handle footer login click
 * Checks if user is already logged in before redirecting
 */
function handleFooterLogin(event) {
  event.preventDefault();
  
  if (isUserLoggedIn()) {
    showAlreadyLoggedInMessage();
  } else {
    window.location.href = '/login.html';
  }
}

/**
 * Handle footer register click
 * Checks if user is already logged in before redirecting
 */
function handleFooterRegister(event) {
  event.preventDefault();
  
  if (isUserLoggedIn()) {
    showAlreadyLoggedInMessage('register');
  } else {
    window.location.href = '/register.html';
  }
}

/**
 * Check if user is logged in using multiple methods
 */
function isUserLoggedIn() {
  // Method 1: Check localStorage
  if (localStorage.getItem('isLoggedIn') === 'true') {
    return true;
  }
  
  // Method 2: Check for user data in localStorage
  if (localStorage.getItem('userEmail') || localStorage.getItem('userName')) {
    return true;
  }
  
  return false;
}

/**
 * Show a message that user is already logged in
 */
function showAlreadyLoggedInMessage(type = 'login') {
  const action = type === 'login' ? 'logged in' : 'registered';
  
  // Create message element
  const messageDiv = document.createElement('div');
  messageDiv.id = 'footerMessage';
  messageDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    z-index: 9999;
    font-family: 'Poppins', sans-serif;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideIn 0.3s ease;
    max-width: 350px;
  `;
  
  // Get user info if available
  const userName = localStorage.getItem('userName') || 'User';
  
  messageDiv.innerHTML = `
    <div style="width:40px;height:40px;background:rgba(255,255,255,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;">
      <i class="fa fa-check-circle" style="font-size: 22px;"></i>
    </div>
    <div style="flex:1;">
      <strong style="font-size: 16px; display:block; margin-bottom:4px;">Already ${action}!</strong>
      <p style="margin: 0; font-size: 13px; opacity: 0.9;">Hello ${userName}, you are already ${action}.</p>
    </div>
    <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; font-size: 20px; cursor: pointer; padding:0 5px;">×</button>
  `;
  
  document.body.appendChild(messageDiv);
  
  // Auto remove after 4 seconds
  setTimeout(() => {
    const msg = document.getElementById('footerMessage');
    if (msg) msg.remove();
  }, 4000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes fadeOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
  renderFooter();
});
