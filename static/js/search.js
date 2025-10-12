let srch_keypress_timer;
var srch_url = "url for the json API";

// id of the form to look for INPUT search elements.
var srch_form_id = "search_form";

// event name for after successfully populating results even if there are none.
const srch_post_populate_results_name = 'srch-post-popultate-results';

// event triggered after the results are added to the page.
const srch_post_popultate_results = new CustomEvent(srch_post_populate_results_name);

// custom click event attached to each new search result.
const srch_result_onclick_name = "srch-result-onclick";

// signal to remove events added to search results.
let srch_abort_controller = new AbortController();

// an array of element ids to use as templates for new items and the destination for those new items.
var result_ids = [
    {
        // An element which will be completely emptied and filled as the searches happen.
        "result_element_id": "search_results_div",

        // A full template of how an individual result should appear.  Elements with "data-field" attributes will
        // have their contents replaced as needed.  The value of "data-field" should match a field in the response
        // JSON.
        "template_id": "search_result_template_div",

        // A full template with content which represents no search results.  This will be copied into
        // "search_results_div" as needed.
        "no_results_template_id": "search_no_result_template_div",
    }
]

function srch_add_result(item_to_add) {
    /*
    * Clones `result_ids[#]["template"]`, fills in the data from `item_to_add`, and adds it to the end of
    * `result_ids[#]["results"]`.
    * :param item_to_add: a dict with the data of the item to add to the results.
    * */
    for (const _result_style of result_ids) {
        const template_elements = srch_get_result_element_template(_result_style);
        for (const template_element of template_elements) {
            let new_result = template_element.cloneNode(true);
            for (const element of new_result.querySelectorAll("[data-field]")) {
                element.innerHTML = item_to_add[element.dataset.field];
            }
            for (const element of new_result.querySelectorAll("[data-href-fn]")) {
                // Sets the href for any element providing a function to convert the id into a url.
                const href_args = srch_get_href_args(element);
                if (Object.keys(href_args).length === 0) {
                    // The non-data-href-arg- way of assuming the only needed value is the "id".
                    element.href = window[element.dataset.hrefFn](item_to_add["id"]);
                } else {
                    // Calling page uses data-href-arg-CUSTOM to specify values to pass to data-href-fn.
                    for (const href_arg_key of Object.keys(href_args)) {
                        // Swapping the name of the field with the value from the current item.
                        href_args[href_arg_key] = item_to_add[href_args[href_arg_key]];
                    }
                    element.href = window[element.dataset.hrefFn](href_args);
                }
            }
            if (item_to_add.hasOwnProperty("id")) {
                new_result.dataset.id = item_to_add["id"];
            }
            new_result.removeAttribute("id");
            srch_get_result_element(_result_style).appendChild(new_result);
            new_result.style.display = "";  // "unsetting" display so it inherits rather than forcing 'block' or 'inline-block'
            for (const element of new_result.getElementsByClassName("search_result_clicky")) {
                // elements are created and removed.  Using CustomEvent so the page has something permanent to listen for.
                element.addEventListener("click", (event) => {
                    element.dispatchEvent(new CustomEvent(srch_result_onclick_name, {bubbles: true}));
                }, {signal: srch_abort_controller.signal});
            }
        }
    }
}

function srch_convert_values_to_query_string(values_to_send) {
    /*
    * :param values_to_send: dict with key "search_terms" to encode.  Optionally includes an "echo" key which is not
    * modified by the API and serves as a way to identify this call.
    * */
    const params = new URLSearchParams();
    for (const pair of values_to_send.search_terms) {
        params.append(pair.key, pair.value);
    }
    if (values_to_send.hasOwnProperty("echo")) {
        params.append("echo", JSON.stringify(values_to_send.echo));
    }
    return params.toString();
}

function srch_filter_keydown(e) {
    /*
    * Filters the keydown event to a specific set of keys.
    * */
    if (srch_key_is_visible(e)) {
        srch_start_timer(e.target);
    } else if (!srch_key_is_not_visible(e)) {
        srch_start_timer(e.target);
    }
}

function srch_get_href_args(element) {
    /*
    Returns the data attributes of element e which are named "data-href-arg-*".
    <a ... data-href-arg-order="x" data-href-arg-line-item="y">
    returns {"order": "x", "line-item": "y"}
    :param e: element containing the "data-href-*" attributes.
    */
    const attributes = {};
    for (let i = 0; i < element.attributes.length; i++) {
        const attribute = element.attributes[i];
        if (attribute.name.startsWith('data-href-arg-')) {
            attributes[attribute.name.slice(14)] = attribute.value;
        }
    }
    return attributes;
}

function srch_get_no_result_element_template(_result_style) {
    /*
    * Returns the element to use as a template when the search returned no results.
    * :param _result_style: dict of a single result style from result_ids.
    * */
    return document.getElementById(_result_style["no_results_template_id"]);
}

function srch_get_result_element(_result_style) {
    /*
    * Returns the element that will be emptied and filled with search results.
    * */
    // TODO: This needs to handle form-named fields.  "{{ widget.attrs.id }}-search-results-div"
    return document.getElementById(_result_style["result_element_id"]);
}

function srch_get_result_element_template(_result_style) {
    /*
    * Gets an element specified by `result_ids[#]["template"]`. This template is of an individual item to be added to
    * result_ids[#]["results"].
    * `result_ids[#]["template"]` can be an array or a single string.  This function will always return an array.
    *
    * :param _result_style: dict of a single result style from result_ids.
    * */
    if (Array.isArray(_result_style["template_id"])) {
        let _srch_result_element_template = [];
        for (const id of _result_style["template_id"]) {
            _srch_result_element_template.push(document.getElementById(id));
        }
        return _srch_result_element_template;
    }
    return [document.getElementById(_result_style["template_id"])];
}

function srch_get_search_elements() {
    /*
    * Returns all elements to be used as search inputs.
    * */
    // console.log(`srch_get_search_elements for srch_form_id = "${srch_form_id}"`);
    const form = document.getElementById(srch_form_id);
    return form.querySelectorAll("[data-search-field]");
}

function srch_get_values_to_send() {
    /*
    * Builds a dict containing the values to search for.  If nothing to use, an `empty` flag is `true`.
    * */
    let values_to_send = {
        empty: true,
        "search_terms": []
    };
    for (const element of srch_get_search_elements()) {
        if (element.value !== "") {
            values_to_send.search_terms.push({key: element.dataset.searchField, value: element.value});
            values_to_send.empty = false;
        }
    }
    return values_to_send;
}

function srch_input_focusout() {
    /*
    * When an input loses focus, clear the timer so the search does not happen.
    * */
    window.clearTimeout(srch_keypress_timer);
}

function srch_key_is_not_visible(e) {
    /*
    * Is the key specified by `e` a non-printing key?
    * */
    let ignore = [
        'ShiftLeft', 'MetaLeft', 'AltLeft', 'ControlLeft',
        'ShiftRight', 'MetaRight', 'AltRight', 'ControlRight',
        'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
        'Enter', 'Tab', 'CapsLock',
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"
    ]
    return ignore.includes(e.code);
}

function srch_key_is_visible(e) {
    /*
    * Is the key specified by `e` a visible key we care about?
    * */
    let donot_ignore = [
        "Backspace", "Space", "Backquote", "Equal", "Minus", "Backslash", "BracketRight", "BracketLeft", "Quote",
        "Semicolon", "Slash", "Period", "Comma",
        "KeyA", "KeyB", "KeyC", "KeyD", "KeyE", "KeyF", "KeyG", "KeyH", "KeyI", "KeyJ", "KeyK", "KeyL", "KeyM",
        "KeyN", "KeyO", "KeyP", "KeyQ", "KeyR", "KeyS", "KeyT", "KeyU", "KeyV", "KeyW", "KeyX", "KeyY", "KeyZ",
        "Digit1", "Digit2", "Digit3", "Digit4", "Digit5", "Digit6", "Digit7", "Digit8", "Digit9", "Digit0",
    ]
    return donot_ignore.includes(e.code);
}

function srch_no_results() {
    /*
    * For each result style defined in result_ids, this removes any existing results and clones the "no results"
    * template into it.
    * */
    srch_remove_all_results();
    for (const _result_style of result_ids) {
        // result_element_id, template_id, no_results_template_id
        let new_result = srch_get_no_result_element_template(_result_style).cloneNode(true);
        srch_get_result_element(_result_style).appendChild(new_result);
        new_result.style.display = "";  // "unsetting" display so it inherits rather than forcing 'block' or 'inline-block'
    }
}

function srch_populate_results(data_packet) {
    /*
    * Given a data packet returned from the API, clear existing results and add in the new ones.
    * Raises a custom event to allow the page to react when searches complete.
    * */
    if (data_packet.data.length === 0) {
        srch_no_results();
        return;
    }
    srch_remove_all_results();
    for (const item of data_packet.data) {
        srch_add_result(item);
    }
    srch_post_popultate_results.detail = data_packet.echo;
    document.dispatchEvent(srch_post_popultate_results);
}

function srch_remove_all_results() {
    /*
    * Clears any existing search results in preparation for either "No results" or new elements.  Does this for all
    * result styles defined in result_ids.
    * Removes any events added to search results.  Replaces the controller since it is a fire-once thing.
    * */
    // TODO: Should each result style have its own abort controller?
    srch_abort_controller.abort();
    srch_abort_controller = new AbortController();

    for (const _result_style of result_ids) {
        let _srch_results_element = srch_get_result_element(_result_style);
        if (_srch_results_element.firstChild === null) {
            return;
        }
        while (_srch_results_element.firstChild) {
            _srch_results_element.removeChild(_srch_results_element.firstChild);
        }
    }
}

function srch_setup_events() {
    /*
    * Adds the event listeners for keys, focus, and click events on the inputs.
    * */
    for (const element of srch_get_search_elements()) {
        if ((element.tagName === "INPUT") && (element.type === "text")) {
            // keydown and focusout events
            element.addEventListener('keydown', (event) => {
                srch_filter_keydown(event);
            });
            element.addEventListener('focusout', (event) => {
                srch_input_focusout();
            });
        }
        if ((element.tagName === "INPUT") && (element.type === "checkbox")) {
            element.addEventListener('onclick', (event) => {
                srch_start_timer(event.target);
            });
        }
    }
}

function srch_start_timer(e) {
    /*
    * Clears any existing timers and starts a new one.  This is used so typing at a "normal" speed will not result in
    * multiple API calls.  Only when there is a more significant pause will an API call happen.
    * */
    window.clearTimeout(srch_keypress_timer);
    srch_keypress_timer = setTimeout(() => {
        srch_timer_elapsed_func(e);
    }, 750);
}

function srch_timer_elapsed_func(caller_obj) {
    /*
    * This is what calls the API specified by `srch_url`.
    * */
    let values_to_send = srch_get_values_to_send();
    if (values_to_send.empty) {
        // nothing to send so don't bother trying.
        srch_no_results();
        return;
    }
    if (caller_obj != null) {
        // In limited cases, the caller_obj is not specified.  Cannot call hasAttributes on null.
        if (caller_obj.hasAttributes("id")) {
            values_to_send["echo"] = {"id": caller_obj.id};
        }
    }
    let query_string = srch_convert_values_to_query_string(values_to_send)
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        let data = JSON.parse(this.responseText);
        srch_populate_results(data);
    }
    xhttp.open("GET", srch_url + "?" + query_string, true);
    xhttp.send();
}

// ready(...) is in not_jquery.js and replaces $( document ).ready(...).
// Using (function() {...})(); doesn't wait for the rest of the page to load.  Setting srch_form_id in the page isn't
// applied yet.
ready(() => {
    /*
    * The page-load function.  The `ready()` function from `not_jquery.js` waits until the page is completely loaded so
    * the page's overriding of the variables at the top are applied.
    * */
    srch_setup_events();
    srch_no_results();
});
