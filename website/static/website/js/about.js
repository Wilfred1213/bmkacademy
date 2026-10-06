document.addEventListener("DOMContentLoaded", function () {

    const revealElements = document.querySelectorAll(
        ".bmk-about-story, " +
        ".bmk-name-section, " +
        ".bmk-beginning, " +
        ".bmk-scl-section, " +
        ".bmk-values-section, " +
        ".bmk-service-section, " +
        ".bmk-commissioning"
    );

    if (!revealElements.length) {
        return;
    }

    const observer = new IntersectionObserver(
        function (entries, observer) {

            entries.forEach(function (entry) {

                if (entry.isIntersecting) {

                    entry.target.classList.add("bmk-reveal-visible");

                    observer.unobserve(entry.target);
                }

            });

        },
        {
            threshold: 0.15
        }
    );

    revealElements.forEach(function (element) {
        element.classList.add("bmk-reveal");
        observer.observe(element);
    });

});