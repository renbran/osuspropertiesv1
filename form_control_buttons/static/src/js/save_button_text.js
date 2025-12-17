/**
 * save_button_text module
 * Replaces icon-only form Save buttons (class o_form_button_save) with plain text label "Save".
 * Also replaces icon-only Cancel buttons (class o_form_button_cancel) with plain text label "Discard".
 * Additionally ensures every save button has highlight styling (oe_highlight + btn btn-primary).
 */
(function () {
    function enforceSaveStyling(btn) {
        if (!btn) return;
        // Guarantee bootstrap / odoo primary classes
        if (!btn.classList.contains('btn')) btn.classList.add('btn');
        if (!btn.classList.contains('btn-primary')) btn.classList.add('btn-primary');
        // Always ensure highlight class (user request)
        if (!btn.classList.contains('oe_highlight')) btn.classList.add('oe_highlight');
    }

    function relabelSave(btn) {
        if (!btn) return;
        const text = btn.textContent.replace(/\s+/g, ' ').trim();
        const hasIcon = btn.querySelector('i, span.o_icon_button_icon');
        // If icon-only (no visible text) replace with plain 'Save'
        if (hasIcon && !text) {
            btn.innerHTML = '';
            btn.append(document.createTextNode('Save'));
        }
        enforceSaveStyling(btn);
    }

    function relabelCancel(btn) {
        if (!btn) return;
        const text = btn.textContent.replace(/\s+/g, ' ').trim();
        const hasIcon = btn.querySelector('i, span.o_icon_button_icon');
        if (hasIcon && !text) {
            btn.innerHTML = '';
            btn.append(document.createTextNode('Discard'));
        }
        // Leave cancel button styling default (do not force highlight)
    }

    function scan(root = document) {
        root.querySelectorAll('button.o_form_button_save').forEach(relabelSave);
        root.querySelectorAll('button.o_form_button_cancel').forEach(relabelCancel);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => scan());
    } else {
        scan();
    }

    const mo = new MutationObserver((mutations) => {
        for (const m of mutations) {
            for (const node of m.addedNodes) {
                if (node.nodeType !== 1) continue;
                if (node.matches) {
                    if (node.matches('button.o_form_button_save')) relabelSave(node);
                    if (node.matches('button.o_form_button_cancel')) relabelCancel(node);
                }
                if (node.querySelectorAll) scan(node);
            }
        }
    });
    mo.observe(document.documentElement, { childList: true, subtree: true });
})();
