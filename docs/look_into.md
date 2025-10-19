# Look Into

These are some tools, methods, ideas that would be good to look into eventually.

## Templates / HTML / Javascript

### Urls in javascript

Sometimes, a url is needed that has a component that isn't known at the time of page load.  This code snippet is
for a url pointing to an admin page for a specific object.  This is called by a button on the selected item in a search
page.  The item's id is not known on page load as the search is done with ajax.  The url is built with a dummy id at
page load and replaced by javascript when needed.

```javascript
function edit_selected_item_button_pressed() {
    let some_url = "{% url "admin:inventory_sourceitem_change" object_id="00000000-0000-0000-0000-000000000000" %}";
    let item_id = $("#calc-item-id").val();
    window.open(some_url.replace("00000000-0000-0000-0000-000000000000", item_id), '_blank').focus();
}
```

An alternative would be to have the search ajax view also return the built url as part of the JSON response.

Or, there's this tool, [django-js-reverse](https://github.com/vintasoftware/django-js-reverse), which seems to have some
way to reverse the urls.  It looks like it compiles a listing of all the urls into a JSON block in its javascript file
during a `collectstatic`.  The javascript calls to reverse a url then use that JSON data to do the work.

Some examples from the readme:

```javascript
Urls.betterlivingGetHouse('house', 12)
Urls['betterliving-get-house']('house', 12)
Urls['namespace:betterliving-get-house']('house', 12)
Urls['betterliving-get-house']({ category_slug: 'house', entry_pk: 12 })
Urls['namespace:betterliving-get-house']({ category_slug: 'house', entry_pk: 12 })
```

You can include/exclude namespaces to help with some security through obscurity.

```python
JS_REVERSE_EXCLUDE_NAMESPACES = ['admin', 'djdt', ...]
JS_REVERSE_INCLUDE_ONLY_NAMESPACES = ['poll', 'calendar', ...]
```

### Do I need jQuery?

Random reading is suggesting many of the things jQuery provided/made easier are now built into vanilla javascript.
Also, since this application has an extremely limited user-base, I don't have to worry about supporting someone still
using IE6.  This site, [You Might Not Need jQuery](https://youmightnotneedjquery.com/), has a variety of "jQuery to JS"
examples.

#### ajax stuff

```javascript
$.getJSON('/my/url', function (data) {});
// vs
const response = await fetch('/my/url');
const data = await response.json();
```

```javascript
$.ajax({
  type: 'POST',
  url: '/my/url',
  data: data
});
// vs
await fetch('/my/url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});
```

```javascript
$.ajax({
  type: 'GET',
  url: '/my/url',
  success: function (resp) {},
  error: function () {}
});
// vs
const response = await fetch('/my/url');

if (!response.ok) {
}

const body = await response.text();
```

#### classes and DOM

```javascript
$(el).addClass(className);
$(el).hasClass(className);
$(el).css(ruleName);
$(el).removeClass(className);
$(el).toggleClass(className);
// vs
el.classList.add(className);
el.classList.contains(className);
getComputedStyle(el)[ruleName];
el.classList.remove(className);
el.classList.toggle(className);
```

```javascript
$(el).clone();
// vs
el.cloneNode(true);
```

```javascript
$(selector).each(function (i, el) {});
// vs
document.querySelectorAll(selector).forEach((el, i) => {});
```

Find elements based on a partial string.
^ matches the start
* matches any position
$ matches the end
```javascript
// starts with "poll-".
document.querySelector('[id^="poll-"]').id;

// starts with "user-" and ends with "-image".
document.querySelector('[id^=user-][id$=-image]').id;
```

```javascript
$(el).empty();
// vs
el.replaceChildren();
```

```javascript
$(el).attr('tabindex');
$(el).removeAttr('tabindex');
$(el).attr('tabindex', 3);
// vs
el.getAttribute('tabindex');
el.removeAttribute('tabindex');
el.setAttribute('tabindex', 3);
```

```javascript
$(el).height();
$(el).width();
// vs
el.getBoundingClientRect().height;
el.getBoundingClientRect().width;
```

```javascript
$(el).parent();
// vs
el.parentNode;
```

```javascript
$(el).val();
// vs
function val(el) {
  if (el.options && el.multiple) {
    return el.options
      .filter((option) => option.selected)
      .map((option) => option.value);
  } else {
    return el.value;
  }
}
```

#### Events

```javascript
$(el).click(function () {});
$(el).off(eventName, eventHandler);
// vs
el.addEventListener('click', () => {});
el.removeEventListener(eventName, eventHandler);
```

```javascript
$(document).on(eventName, elementSelector, handler);
// vs
document.addEventListener(eventName, (event) => {
  if (event.target.closest(elementSelector)) {
    handler.call(event.target, event);
  }
});
```

```javascript
$(el).on(eventName, eventHandler);
// Or when you want to delegate event handling
$(el).on(eventName, selector, eventHandler);
// vs
function addEventListener(el, eventName, eventHandler, selector) {
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

// Use the return value to remove that event listener, see #off
addEventListener(el, eventName, eventHandler);
// Or when you want to delegate event handling
addEventListener(el, eventName, eventHandler, selector);
```

```javascript
$(document).ready(function () {});
// vs
function ready(fn) {
  if (document.readyState !== 'loading') {
    fn();
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}
```

Custom event

```javascript
$(el).trigger('my-event', {some: 'data'});
// vs
const event = new CustomEvent('my-event', {detail: {some: 'data'}});
el.dispatchEvent(event);
```

Native event

```javascript
$(el).trigger('focus');
// vs
function trigger(el, eventType) {
  if (typeof eventType === 'string' && typeof el[eventType] === 'function') {
    el[eventType]();
  } else {
    const event =
      typeof eventType === 'string'
        ? new Event(eventType, {bubbles: true})
        : eventType;
    el.dispatchEvent(event);
  }
}
trigger(el, 'focus');
// For a full list of event types: https://developer.mozilla.org/en-US/docs/Web/API/Event
trigger(el, new PointerEvent('pointerover'));
```

#### Utils

```javascript
$.each(array, function (i, item) {});
// vs
array.forEach((item, i) => {});
```

```javascript
$.isArray(arr);
// vs
Array.isArray(arr);
```

```javascript
$.isNumeric(val);
// vs
function isNumeric(num) {
  if (typeof num === 'number') return num - num === 0;
  if (typeof num === 'string' && num.trim() !== '')
    return Number.isFinite(+num);
  return false;
}
isNumeric(val);
```

```javascript
$.each(obj, function (key, value) {});
// vs
for (const [key, value] of Object.entries(obj)) {}
```

```javascript
$.parseJSON(string);
// vs
JSON.parse(string);
```

```javascript
$.trim(string);
// vs
string.trim();
```

```javascript
$.type(obj);
// vs
Object.prototype.toString
  .call(obj)
  .replace(/^\[object (.+)\]$/, '$1')
  .toLowerCase();
```

### CSS

[CSS Flexbox](https://internetingishard.netlify.app/html-and-css/flexbox/)
[Aligning items in a flex container](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Aligning_items_in_a_flex_container)

* Use display: flex; to create a flex container.
* Use justify-content to define the horizontal alignment of items.
* Use align-items to define the vertical alignment of items.
* Use flex-direction if you need columns instead of rows.
* Use the row-reverse or column-reverse values to flip item order.
* Use order to customize the order of individual elements.
* Use align-self to vertically align individual items.
* Use flex to create flexible boxes that can stretch and shrink.


## Issues

* Single purchased item is a variety pack.  How do we split that to track the items?
  * "lemon, lime, orange jello" needs to add quantity of 3 types of gelatin.
* Items which don't need inventoried.
  * things that appear on broulims receipts like newspapers, Tuesday lunch/board snacks, etc.
* Same SourceItem appearing twice on the same Order.
  * I believe there was an order with a full pack of lettuce and a split pack of the same lettuce.  Pretty sure it
    showed two line items on the order.
