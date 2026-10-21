document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector("[data-nav-toggle]");
    const panel = document.querySelector("[data-nav-panel]");
    const backdrop = document.querySelector("[data-nav-backdrop]");
    const closeButton = document.querySelector("[data-nav-close]");

    if (!toggle || !panel || !backdrop || !closeButton) return;

    const desktopNavigation = window.matchMedia("(min-width: 64rem)");
    let isOpen = false;

    function openMenu() {
        if (isOpen || desktopNavigation.matches) return;
        isOpen = true;
        panel.inert = false;
        panel.classList.remove("-translate-x-full");
        panel.classList.add("translate-x-0");
        backdrop.classList.remove("hidden");
        // Allow the backdrop to transition from transparent.
        requestAnimationFrame(() => {
            if (!isOpen) return;
            backdrop.classList.remove("opacity-0");
            backdrop.classList.add("opacity-100");
        });

        toggle.setAttribute("aria-expanded", "true");
        toggle.classList.add("invisible");

        document.body.classList.add("overflow-hidden");
        closeButton.focus({ preventScroll: true });
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
        toggle.classList.remove("invisible");

        document.body.classList.remove("overflow-hidden");

        if (panel.contains(document.activeElement) || document.activeElement === toggle) {
            const focusTarget = desktopNavigation.matches
                ? document.querySelector("[data-nav-desktop] a")
                : toggle;
            focusTarget?.focus();
        }

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
    closeButton.addEventListener("click", closeMenu);

    desktopNavigation.addEventListener("change", () => {
        if (desktopNavigation.matches) closeMenu();
    });

    document.addEventListener("keydown", (event) => {
        if (!isOpen) return;
        if (event.key === "Escape") {
            closeMenu();
            toggle.focus();
        }
        if (event.key === "Tab") {
            const links = panel.querySelectorAll("a");
            const lastLink = links[links.length - 1];
            if (event.shiftKey && document.activeElement === closeButton) {
                event.preventDefault();
                lastLink?.focus();
            } else if (!event.shiftKey && document.activeElement === lastLink) {
                event.preventDefault();
                closeButton.focus();
            }
        }
    });

    panel.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });
})