
document.addEventListener("DOMContentLoaded", function () {

    const modalElement = document.getElementById(
        "schoolEventModal"
    );

    if (!modalElement) {
        return;
    }


    const eventModal = new bootstrap.Modal(
        modalElement
    );


    eventModal.show();


    modalElement.addEventListener(
        "hidden.bs.modal",
        function () {

            document.body.classList.remove(
                "modal-open"
            );


            document.body.style.removeProperty(
                "overflow"
            );


            document.body.style.removeProperty(
                "padding-right"
            );


            const backdrops =
                document.querySelectorAll(
                    ".modal-backdrop"
                );


            backdrops.forEach(
                function (backdrop) {

                    backdrop.remove();

                }
            );

        }
    );

});

document.addEventListener("DOMContentLoaded", function () {

    const heroCarousel = document.getElementById(
        "bmkHeroCarousel"
    );

    if (!heroCarousel) {
        return;
    }


    function animateHeroContent() {

        const activeSlide =
            heroCarousel.querySelector(
                ".carousel-item.active"
            );

        if (!activeSlide) {
            return;
        }


        const content =
            activeSlide.querySelector(
                ".bmk-hero-content"
            );

        if (!content) {
            return;
        }


        content.classList.remove(
            "bmk-hero-content-animate"
        );


        /*
            * Force browser reflow so the animation
            * can restart every time.
            */

        void content.offsetWidth;


        content.classList.add(
            "bmk-hero-content-animate"
        );
    }


    /*
        * Animate the first slide.
        */

    animateHeroContent();


    /*
        * Animate every new slide.
        */

    heroCarousel.addEventListener(
        "slid.bs.carousel",
        animateHeroContent
    );

});



document.addEventListener("DOMContentLoaded", function () {

    const journeyElements = document.querySelectorAll(
        ".bmk-journey-card, " +
        ".bmk-journey-bottom"
    );

    const academicsSection = document.querySelector(
        ".bmk-academics"
    );
    const gallerySection = document.querySelector(
        ".bmk-gallery-section"
    );
    const upcomingEventsSection = document.querySelector(
        ".bmk-upcoming-events"
    );
    const admissionsSection = document.querySelector(
        ".bmk-admissions"
    );


    /* =========================================
        JOURNEY REVEAL
    ========================================= */

    if (journeyElements.length) {

        const journeyObserver = new IntersectionObserver(
            function (entries, observer) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add(
                            "bmk-card-visible"
                        );

                        observer.unobserve(entry.target);
                    }

                });

            },
            {
                threshold: 0.15
            }
        );

        journeyElements.forEach(function (element) {
            journeyObserver.observe(element);
        });
    }


    /* =========================================
        ACADEMICS REVEAL
    ========================================= */

    if (academicsSection) {

        const academicsObserver = new IntersectionObserver(
            function (entries, observer) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add(
                            "bmk-academics-visible"
                        );

                        observer.unobserve(entry.target);
                    }

                });

            },
            {
                threshold: 0.15
            }
        );

        academicsObserver.observe(academicsSection);
    }

    /* =========================================
    GALLERY REVEAL
    ========================================= */

    if (gallerySection) {

        const galleryObserver = new IntersectionObserver(
            function (entries, observer) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add(
                            "bmk-gallery-visible"
                        );

                        observer.unobserve(entry.target);
                    }

                });

            },
            {
                threshold: 0.15
            }
        );

        galleryObserver.observe(gallerySection);
    }
    /* =========================================
    UPCOMING EVENTS REVEAL
    ========================================= */

    if (upcomingEventsSection) {

        const eventElements =
            upcomingEventsSection.querySelectorAll(
                ".bmk-event-card, .bmk-events-heading"
            );

        const eventsObserver = new IntersectionObserver(
            function (entries, observer) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add(
                            "bmk-event-visible"
                        );

                        observer.unobserve(entry.target);
                    }

                });

            },
            {
                threshold: 0.15
            }
        );

        eventElements.forEach(function (element) {
            eventsObserver.observe(element);
        });
    }
    /* =========================================
    ADMISSIONS REVEAL
    ========================================= */

    if (admissionsSection) {

        const admissionsObserver = new IntersectionObserver(
            function (entries, observer) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add(
                            "bmk-admissions-visible"
                        );

                        observer.unobserve(entry.target);
                    }

                });

            },
            {
                threshold: 0.15
            }
        );

        admissionsObserver.observe(admissionsSection);
    }
    const contactSection = document.querySelector(".bmk-contact");

    if (contactSection) {

        const contactElements = contactSection.querySelectorAll(
            ".row.justify-content-center, " +
            ".bmk-contact-card, " +
            ".bmk-contact-message"
        );

        const contactObserver = new IntersectionObserver(
            function (entries, observer) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add(
                            "bmk-contact-visible"
                        );

                        observer.unobserve(entry.target);
                    }

                });

            },
            {
                threshold: 0.15
            }
        );

        contactElements.forEach(function (element) {
            contactObserver.observe(element);
        });
    }
    const safeguardingSection = document.querySelector(
        ".bmk-safeguarding"
    );
    
    if (safeguardingSection) {
    
        const safeguardingObserver = new IntersectionObserver(
            function (entries, observer) {
    
                entries.forEach(function (entry) {
    
                    if (entry.isIntersecting) {
    
                        entry.target.classList.add(
                            "bmk-safeguarding-visible"
                        );
    
                        observer.unobserve(entry.target);
                    }
    
                });
    
            },
            {
                threshold: 0.15
            }
        );
    
        safeguardingObserver.observe(safeguardingSection);
    }
});

