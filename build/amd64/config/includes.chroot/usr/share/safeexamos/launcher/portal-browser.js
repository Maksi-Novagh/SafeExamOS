/* Portal access is not exam lockdown. This script only constructs a
 * canonical login URL from an administrator-approved portal catalog.
 * Chromium's managed URLAllowlist is the enforcement boundary.
 */
(function () {
  'use strict';
  const catalog = window.SAFEEXAMOS_PORTALS;
  const select = document.getElementById('portal-choice');
  const schoolRow = document.getElementById('smartschool-row');
  const school = document.getElementById('smartschool-school');
  const button = document.getElementById('open-portal');
  const status = document.getElementById('portal-status');
  const examStatus = document.getElementById('compat-status');
  if (!catalog || catalog.schema_version !== 1 || !Array.isArray(catalog.portals)) {
    status.textContent = 'Administrator portal catalog unavailable.';
    button.disabled = true;
    return;
  }
  const allowedKinds = new Set(['smartschool', 'fixed']);
  const entries = catalog.portals.filter(p => p && typeof p.id === 'string' &&
    allowedKinds.has(p.kind) && typeof p.label === 'string');
  if (entries.length === 0) {
    status.textContent = 'No school portals are configured.';
    button.disabled = true;
    return;
  }
  entries.forEach(portal => {
    const option = document.createElement('option');
    option.value = portal.id;
    option.textContent = portal.label;
    select.appendChild(option);
  });

  function current() { return entries.find(p => p.id === select.value); }
  function refresh() {
    const portal = current();
    schoolRow.hidden = !portal || portal.kind !== 'smartschool';
    status.textContent = 'This is a pre-exam school portal, not a secured examination.';
  }

  function smartschoolURL(value) {
    const text = value.trim().toLowerCase();
    // Users may supply the school's short Smartschool platform code or its
    // canonical full hostname, but never a generic URL or a second domain.
    const host = text.endsWith('.smartschool.be') ?
      text.slice(0, -'.smartschool.be'.length) : text;
    if (!/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(host)) {
      throw new Error('Enter the short school platform name, e.g. myschool.');
    }
    return 'https://' + host + '.smartschool.be/';
  }

  button.addEventListener('click', function () {
    const portal = current();
    if (!portal) return;
    if (examStatus.textContent === 'Blocking') {
      status.textContent = 'System pre-flight must finish before opening a school portal.';
      return;
    }
    let target;
    try {
      if (portal.kind === 'smartschool') {
        target = smartschoolURL(school.value);
      } else {
        // Admin-generated configuration, not user-supplied navigation.
        target = portal.start_url;
        const url = new URL(target);
        if (url.protocol !== 'https:' || url.username || url.password) {
          throw new Error('Invalid administrator portal configuration.');
        }
      }
    } catch (error) {
      status.textContent = error.message;
      return;
    }
    status.textContent = 'Opening approved portal…';
    window.location.assign(target);
  });
  select.addEventListener('change', refresh);
  refresh();
})();
