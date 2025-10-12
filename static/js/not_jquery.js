// Some javascript that helps with not having to load jquery.
function altAddEventListener(el, eventName, eventHandler, selector) {
  if (selector) {
    const wrappedHandler = (e) => {
      if (!e.target) return;
      const el = e.target.closest(selector);
      if (el) {
        eventHandler.call(el, e);
      }
    };
    el.addEventListener(eventName, wrappedHandler);
    return wrappedHandler;
  } else {
    const wrappedHandler = (e) => {
      eventHandler.call(el, e);
    };
    el.addEventListener(eventName, wrappedHandler);
    return wrappedHandler;
  }
}

// Converts a camelCaseString to snake_case_string.
// Would like to add some customizations to handle "ID" and possibly arbitrary initialisms.
const camelToSnakeCase = str => str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);

function generateElements(html) {
  const template = document.createElement('template');
  template.innerHTML = html.trim();
  // Returns a collection or something.  Had to add [0] when using this to create <option> elements for a <select>.
  return template.content.children;
}

function getType(obj) {
    return Object.prototype.toString
      .call(obj)
      .replace(/^\[object (.+)\]$/, '$1')
      .toLowerCase();
}

function isNumeric(num) {
  if (typeof num === 'number') return num - num === 0;
  if (typeof num === 'string' && num.trim() !== '')
    return Number.isFinite(+num);
  return false;
}

// Simple test if the val_to_test is a string or not.
const isString = val_to_test => typeof val_to_test === 'string' || val_to_test instanceof String;

function ready(fn) {
  if (document.readyState !== 'loading') {
    fn();
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}

function val(el) {
  if (el.options && el.multiple) {
    return el.options
      .filter((option) => option.selected)
      .map((option) => option.value);
  } else {
    return el.value;
  }
}
