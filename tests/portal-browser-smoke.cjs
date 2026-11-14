#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const root = 'build/amd64/config/includes.chroot/usr/share/safeexamos/launcher/';
const script = fs.readFileSync(root + 'portal-browser.js', 'utf8');
const catalog = fs.readFileSync(root + 'portals.js', 'utf8');
const html = fs.readFileSync(root + 'index.html', 'utf8');
assert.match(html, /id="portal-choice"/);
assert.match(html, /id="smartschool-school"/);
assert.match(html, /src="portal-browser\.js"/);

function browser() {
  const elements = new Map(), navigations = [];
  function get(id) {
    if (!elements.has(id)) {
      elements.set(id, {
        hidden: false, value: '', textContent: '', disabled: false,
        handlers: {}, options: [],
        appendChild(child) {
          this.options.push(child);
          if (this.options.length === 1) this.value = child.value;
        },
        addEventListener(name, callback) { this.handlers[name] = callback; },
        click() { this.handlers.click(); }
      });
    }
    return elements.get(id);
  }
  const context = {
    window: {location: {assign(target) { navigations.push(target); }}},
    document: {getElementById: get, createElement() {return {value: '', textContent: ''};}},
    URL
  };
  get('compat-status').textContent = 'Supported';
  vm.createContext(context);
  vm.runInContext(catalog, context);
  vm.runInContext(script, context);
  return {get, navigations};
}
const b = browser();
assert.equal(b.get('portal-choice').value, 'smartschool');
b.get('smartschool-school').value = 'mYschool';
b.get('open-portal').click();
assert.deepEqual(b.navigations, ['https://myschool.smartschool.be/']);
b.get('smartschool-school').value = 'https://evil.example/';
b.get('open-portal').click();
assert.equal(b.navigations.length, 1);
assert.match(b.get('portal-status').textContent, /school platform name/);
b.get('smartschool-school').value = 'school.smartschool.be';
b.get('open-portal').click();
assert.equal(b.navigations[1], 'https://school.smartschool.be/');
b.get('compat-status').textContent = 'Blocking';
b.get('open-portal').click();
assert.equal(b.navigations.length, 2);
assert.match(b.get('portal-status').textContent, /pre-flight/);

console.log('Portal browser fixture PASS: Smartschool, canonical host, rejected arbitrary URL, fail-closed state');
