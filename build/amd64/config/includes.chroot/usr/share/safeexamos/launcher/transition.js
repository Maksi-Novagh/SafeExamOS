/* Only the local SafeExamOS UI can request a mode transition.
 * The token is embedded by the loopback-only supervisor in served HTML.
 * This is not an authentication mechanism for a production exam server.
 */
(function () {
  'use strict';
  const token = document.querySelector('meta[name="safeexamos-transition-token"]')?.content;
  window.SafeExamNativeLabEnabled = false;
  fetch('/api/status', {cache: 'no-store', credentials: 'same-origin'})
    .then(r => r.ok ? r.json() : null)
    .then(data => { window.SafeExamNativeLabEnabled = !!(data && data.native_lab_enabled && data.mode === 'portal'); })
    .catch(() => {});
  window.SafeExamTransition = Object.freeze({
    async request(action) {
      if (!token || !['start-demo', 'finish-demo', 'start-native-lab'].includes(action)) {
        throw new Error('Local session transition unavailable');
      }
      const result = await fetch('/api/transition', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-SafeExamOS-Token': token
        },
        credentials: 'same-origin',
        cache: 'no-store',
        body: JSON.stringify({action})
      });
      if (!result.ok) throw new Error('Transition was not accepted');
      // The supervisor stops this browser and starts the other isolated profile.
      return true;
    }
  });
})();
