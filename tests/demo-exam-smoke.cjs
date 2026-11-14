#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const base = path.join(root, 'build/amd64/config/includes.chroot/usr/share/safeexamos/launcher');
const demo = require(path.join(base, 'demo-exam.js'));
const html = fs.readFileSync(path.join(base, 'demo.html'), 'utf8');

assert.match(html, /<script src="demo-exam\.js"><\/script>/);
assert.match(html, /SafeExamDemo\.mount\(document,window\)/);
assert.match(html, /DEMO ONLY/);
assert.equal(demo.QUESTIONS.length, 4);
assert.doesNotMatch(html + fs.readFileSync(path.join(base, 'demo-exam.js'), 'utf8'),
  /(?:fetch\s*\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage|indexedDB)/);

const model = demo.createSession();
assert.equal(model.phase, 'questions');
assert.equal(model.summary().answered, 0);
assert.equal(model.move(-1), false);
assert.throws(() => model.select(99), /Invalid option/);
model.select(1);
assert.equal(model.summary().answered, 1);
assert.equal(model.move(1), true);
model.select(0);
assert.equal(model.summary().answered, 2);
model.review();
assert.equal(model.phase, 'review');
assert.equal(model.reviewItems()[1].answered, true);
assert.throws(() => model.select(0), /Invalid demo session transition/);
model.resume();
assert.equal(model.phase, 'questions');
model.review();
const receipt = model.submit();
assert.deepEqual(receipt, {answered: 2, total: 4, unanswered: 2});
assert.equal(model.phase, 'submitted');
assert.equal(model.answer, null, 'answers must be cleared on local submission');
assert.throws(() => model.submit(), /Invalid demo session transition/);

class FakeElement {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this.handlers = {};
    this.hidden = false;
    this.disabled = false;
    this.checked = false;
    this.value = '';
    this.textContent = '';
  }
  get firstChild() { return this.children[0] || null; }
  appendChild(child) { this.children.push(child); }
  removeChild(child) {
    const i = this.children.indexOf(child);
    assert.ok(i >= 0);
    this.children.splice(i, 1);
  }
  addEventListener(event, fn) { this.handlers[event] = fn; }
  click() {
    assert.ok(this.handlers.click, 'missing click listener');
    this.handlers.click();
  }
}
function fakeDOM() {
  const ids = new Map();
  return {
    getElementById(id) {
      if (!ids.has(id)) ids.set(id, new FakeElement(id));
      return ids.get(id);
    },
    createElement(tag) { return new FakeElement(tag); }
  };
}
const doc = fakeDOM();
const redirects = [];
const host = {SafeExamTransition: {request(action) { redirects.push(action); return Promise.resolve(true); }}};
const uiSession = demo.mount(doc, host);
const get = id => doc.getElementById(id);
assert.equal(get('demo-question-number').textContent, 'Question 1 of 4');
assert.equal(get('demo-options').children.length, 3);
assert.equal(get('demo-prev').disabled, true);
get('demo-options').children[1].children[0].handlers.change();
assert.equal(uiSession.summary().answered, 1);
assert.equal(get('demo-progress-text').textContent, '1 of 4 answered');
get('demo-next').click();
assert.equal(get('demo-question-number').textContent, 'Question 2 of 4');
get('demo-review').click();
assert.equal(get('review-panel').hidden, false);
assert.match(get('demo-review-summary').textContent, /3 unanswered/);
get('demo-resume').click();
assert.equal(get('question-panel').hidden, false);
get('demo-exit').click();
assert.equal(get('discard-panel').hidden, false);
get('demo-stay').click();
assert.equal(get('question-panel').hidden, false);
get('demo-review').click();
get('demo-submit').click();
assert.equal(get('receipt-panel').hidden, false);
assert.match(get('demo-receipt-text').textContent, /No answers were uploaded/);
assert.equal(uiSession.summary().answered, 1);
get('demo-done').click();
assert.deepEqual(redirects, ['finish-demo']);

const discardDoc = fakeDOM(), discardHost = {SafeExamTransition: {request(action) { redirects.push(action); return Promise.resolve(true); }}};
demo.mount(discardDoc, discardHost);
discardDoc.getElementById('demo-exit').click();
discardDoc.getElementById('demo-discard').click();
assert.deepEqual(redirects, ['finish-demo', 'finish-demo']);

console.log('Offline demo exam PASS: questions, navigation, review, submission, data clearing and exit');
