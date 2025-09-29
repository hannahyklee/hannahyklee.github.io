function updateCarouselButtons(container) {
    const carousel = container.querySelector('.image-carousel');
    const prevBtn = container.querySelector('.carousel-prev');
    const nextBtn = container.querySelector('.carousel-next');
    
    // Check if at beginning or end
    prevBtn.disabled = carousel.scrollLeft <= 0;
    nextBtn.disabled = carousel.scrollLeft >= (carousel.scrollWidth - carousel.clientWidth);
}

function getImageScrollDistance(carousel) {
    // Get the computed style to access the gap value
    const computedStyle = getComputedStyle(carousel);
    const gap = parseFloat(computedStyle.gap) || 4; // 0.25rem = 4px, fallback to 4px
    
    const imageWrapper = carousel.querySelector('.carousel-image-wrapper');
    if (!imageWrapper) return 300; // fallback
    
    const imageWidth = imageWrapper.offsetWidth;
    return imageWidth + gap;
}

function scrollCarousel(container, direction) {
    const carousel = container.querySelector('.image-carousel');
    const scrollDistance = getImageScrollDistance(carousel);
    const currentScroll = carousel.scrollLeft;
    
    const newScrollPosition = direction === 'next' 
        ? currentScroll + scrollDistance 
        : currentScroll - scrollDistance;
    
    carousel.scrollTo({
        left: newScrollPosition,
        behavior: 'smooth'
    });
}

// Initialize all carousels when page loads
document.addEventListener('DOMContentLoaded', function() {
    const carousels = document.querySelectorAll('.image-carousel-container');
    
    carousels.forEach(container => {
        const carousel = container.querySelector('.image-carousel');
        const prevBtn = container.querySelector('.carousel-prev');
        const nextBtn = container.querySelector('.carousel-next');
        
        // Initial button state
        updateCarouselButtons(container);
        
        // Update buttons on scroll
        carousel.addEventListener('scroll', () => updateCarouselButtons(container));
        
        // Add click handlers for navigation buttons
        prevBtn.addEventListener('click', () => scrollCarousel(container, 'prev'));
        nextBtn.addEventListener('click', () => scrollCarousel(container, 'next'));
    });
});