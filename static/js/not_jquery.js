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

function getNextTabStop(el, include_a_href=false) {
    /*
    * Returns the element after `el` or the first element if `el` isn't actually a form element.
    * */
    // get all likely tabable elements
    let form = el.closest('form');
    // Removed "a[href]" by default from the selectors as I don't want focus on links.
    let selectors = 'input:not([type=hidden]), button, select, textarea';
    if (include_a_href) {
        selectors += ', a[href]'
    }
    let universe = form.querySelectorAll(selectors);
    // TODO: filter out hidden fields.  Check https://github.com/focus-trap/tabbable/blob/master/src/index.js
    // filter to only those with a >=0 tabIndex
    let list = Array.prototype.filter.call(universe, function(item) {return item.tabIndex >= "0"});
    // find the index of the passed-in element
    let index = list.indexOf(el);
    // return the next element or, if that doesn't work, the first element.
    return list[index + 1] || list[0];
}

function getType(obj) {
    return Object.prototype.toString
      .call(obj)
      .replace(/^\[object (.+)\]$/, '$1')
      .toLowerCase();
}

function isFormset(e) {
    /*
    * Given any element in the form, return True if the current form is a formset.  False if not.
    * */
    // Get to the form from any input element within the form.
    let form_element = document.getElementById(e).form;
    return !!(form_element.querySelector('[name$="TOTAL_FORMS"]'));
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

function queryElementContains(selector, text) {
    return queryElementContainsAll(selector, text)[0];
}

function queryElementContainsAll(selector, text) {
    /*
    * queryElementContainsAll('div', 'sometext'); // find "div" that contain "sometext"
    * queryElementContainsAll('div', /^sometext/); // find "div" that start with "sometext"
    * queryElementContainsAll('div', /sometext$/i); // find "div" that end with "sometext", case-insensitive
    * */
    // Started from https://stackoverflow.com/a/37098508
    let elements = document.querySelectorAll(selector);
    return Array.prototype.filter.call(elements, function(element){
        return RegExp(text).test(element.textContent);
    });
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
