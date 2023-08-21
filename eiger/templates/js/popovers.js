function initializePopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('.popover-icon'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Close open popovers when a new one is displayed
    popoverTriggerList.forEach(function (popoverTriggerEl) {
        popoverTriggerEl.addEventListener('click', function () {
            popoverList.forEach(function (popover) {
                popover.hide();
            });
        });
    });

    // Close popovers when clicking anywhere on the screen
    document.body.addEventListener('click', function () {
        popoverList.forEach(function (popover) {
            popover.hide();
        });
    });

    // Automatically close popovers after a specified duration
    popoverTriggerList.forEach(function (popoverTriggerEl) {
        popoverTriggerEl.addEventListener('shown.bs.popover', function () {
            var popover = bootstrap.Popover.getInstance(popoverTriggerEl);
            var popoverDuration = popoverTriggerEl.getAttribute('data-popover-duration');
            if (popoverDuration) {
                setTimeout(function () {
                    popover.hide();
                }, popoverDuration);
            }
        });
    });
}

// Initialize popovers when the DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    initializePopovers();
});
