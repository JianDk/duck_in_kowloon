document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-nav-toggle]");
    const panel = document.querySelector("[data-nav-panel]");
    const backdrop = document.querySelector("[data-nav-backdrop]");
    const openIcon = document.querySelector("[data-menu-open-icon]");
    const closeIcon = document.querySelector("[data-menu-close-icon]");

    if (!toggle || !panel || !backdrop) return;

    let isOpen = false;
    
    function openMenu() {
        if (isOpen) return;
        isOpen = true;
        panel.inert = false;
        panel.classList.remove("-translate-x-full");
        panel.classList.add("translate-x-0");
        backdrop.classList.remove("hidden");
        // Allow the backdrop to transition from transparent.
        requestAnimationFrame(() => {
            backdrop.classList.remove("opacity-0");
            backdrop.classList.add("opacity-100");
        });

        toggle.setAttribute("aria-expanded", "true");
        toggle.setAttribute("aria-label", "Close navigation");

        openIcon.classList.add("hidden");
        closeIcon.classList.remove("hidden");

        document.body.classList.add("overflow-hidden");
    }

    function closeMenu() {
        if (!isOpen) return;
        isOpen = false;

        panel.classList.add("-translate-x-full");
        panel.classList.remove("translate-x-0");
        panel.inert = true;

        backdrop.classList.add("opacity-0");
        backdrop.classList.remove("opacity-100");

        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open navigation");

        openIcon.classList.remove("hidden");
        closeIcon.classList.add("hidden");

        document.body.classList.remove("overflow-hidden");

        // Wait until the backdrop fade-out finishes.
        window.setTimeout(() => {
            if (!isOpen) {
                backdrop.classList.add("hidden");
            }
        }, 300);
    }

    toggle.addEventListener("click", () => {
        isOpen ? closeMenu() : openMenu();
    });

    backdrop.addEventListener("click", closeMenu);

    panel.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });
})