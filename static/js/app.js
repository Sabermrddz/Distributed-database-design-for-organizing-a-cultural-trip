/* JavaScript for Cultural Trip Database */

// Toggle mobile menu
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu') || document.querySelector('.mobile-menu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'DZD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Show alert notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Form validation
function validateBookingForm(formData) {
    if (!formData.name || formData.name.trim() === '') {
        showNotification('Please enter your name', 'error');
        return false;
    }
    
    if (!formData.nationality || formData.nationality.trim() === '') {
        showNotification('Please enter your nationality', 'error');
        return false;
    }
    
    if (!formData.contact || formData.contact.trim() === '') {
        showNotification('Please enter your contact information', 'error');
        return false;
    }
    
    if (!formData.trip_id || formData.trip_id === '') {
        showNotification('Please select a trip', 'error');
        return false;
    }
    
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
        showNotification('Please enter a valid amount', 'error');
        return false;
    }
    
    return true;
}

// Load trips dynamically
async function loadTrips(region = null) {
    try {
        let url = '/api/trips/';
        if (region) {
            url += `?region=${region}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            renderTrips(data.trips);
        } else {
            showNotification('Error loading trips', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to load trips', 'error');
    }
}

// Render trips list
function renderTrips(trips) {
    const container = document.getElementById('trips-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (trips.length === 0) {
        container.innerHTML = '<p class="text-gray-600">No trips found.</p>';
        return;
    }
    
    trips.forEach(trip => {
        const tripCard = createTripCard(trip);
        container.appendChild(tripCard);
    });
}

// Create trip card element
function createTripCard(trip) {
    const card = document.createElement('div');
    card.className = 'trip-card bg-white rounded-lg shadow-md overflow-hidden';
    
    card.innerHTML = `
        <div class="bg-gradient-to-r from-purple-500 to-pink-600 h-40 flex items-center justify-center">
            <i class="fas fa-suitcase-rolling text-white text-5xl"></i>
        </div>
        <div class="p-6">
            <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                ${trip.region}
            </span>
            <h3 class="text-xl font-bold mt-2 mb-2">Trip #${trip.id}</h3>
            <p class="text-gray-600 text-sm mb-4">
                <i class="fas fa-calendar"></i> ${formatDate(trip.start_date)} to ${formatDate(trip.end_date)}
            </p>
            <a href="/trips/${trip.id}/" class="text-purple-600 font-semibold hover:text-purple-800">
                View Details <i class="fas fa-arrow-right"></i>
            </a>
        </div>
    `;
    
    return card;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add active state to navigation
    const currentLocation = location.pathname;
    const menuItems = document.querySelectorAll('nav a');
    menuItems.forEach(item => {
        if (item.getAttribute('href') === currentLocation) {
            item.classList.add('font-bold', 'text-white');
        }
    });

    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenu) {
        mobileMenu.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
            });
        });
    }
});

// Export functions for use
window.CulturalTrips = {
    formatCurrency,
    formatDate,
    showNotification,
    validateBookingForm,
    loadTrips,
    renderTrips,
    createTripCard,
    toggleMobileMenu
};
