"use strict";

/* ============================================================
   BLACKBIRD — DUAL MODE
============================================================ */

const dualHero = document.querySelector(".dual-hero");
const coderPanel = document.querySelector(".dual-panel--coder");
const adminPanel = document.querySelector(".dual-panel--admin");


if (dualHero && coderPanel && adminPanel) {

    const desktopMode = window.matchMedia("(min-width: 901px)");


    /* --------------------------------------------------------
       RESET
    --------------------------------------------------------- */

    const resetDualMode = () => {
        dualHero.classList.remove(
            "is-coder-active",
            "is-admin-active"
        );
    };


    /* --------------------------------------------------------
       CODER
    --------------------------------------------------------- */

    const activateCoder = () => {
        if (!desktopMode.matches) {
            return;
        }

        dualHero.classList.remove("is-admin-active");
        dualHero.classList.add("is-coder-active");
    };


    /* --------------------------------------------------------
       ADMIN SYS
    --------------------------------------------------------- */

    const activateAdmin = () => {
        if (!desktopMode.matches) {
            return;
        }

        dualHero.classList.remove("is-coder-active");
        dualHero.classList.add("is-admin-active");
    };


    /* --------------------------------------------------------
       MOUSE / POINTER
    --------------------------------------------------------- */

    coderPanel.addEventListener(
        "pointerenter",
        activateCoder
    );

    adminPanel.addEventListener(
        "pointerenter",
        activateAdmin
    );

    dualHero.addEventListener(
        "pointerleave",
        resetDualMode
    );


    /* --------------------------------------------------------
       KEYBOARD ACCESSIBILITY
    --------------------------------------------------------- */

    coderPanel.addEventListener(
        "focusin",
        activateCoder
    );

    adminPanel.addEventListener(
        "focusin",
        activateAdmin
    );


    dualHero.addEventListener(
        "focusout",
        (event) => {

            const nextFocusedElement = event.relatedTarget;

            if (
                !nextFocusedElement ||
                !dualHero.contains(nextFocusedElement)
            ) {
                resetDualMode();
            }

        }
    );


    /* --------------------------------------------------------
       WINDOW RESIZE
    --------------------------------------------------------- */

    desktopMode.addEventListener(
        "change",
        resetDualMode
    );
}