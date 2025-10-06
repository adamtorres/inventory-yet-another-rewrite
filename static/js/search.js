let srch_keypress_timer;
var srch_url = "url for the json API";

// Matches the keys in result_style_ids.  Only those in this list will be populated with search results.
var active_result_styles = ["div"];

var srch_form_id = "search_form";

const srch_post_populate_results_name = 'srch-post-popultate-results';

// event triggered after the results are added to the page.
const srch_post_popultate_results = new CustomEvent(srch_post_populate_results_name);

// custom click event attached to each new search result.
const srch_result_onclick_name = "srch-result-onclick";

let srch_abort_controller = new AbortController();

var result_style_ids = {
    // The value of the key is arbitrary.  It just represents one of the output styles.
    "div": {
        //A containing element, usually a div, which wholly contains everything for this result type.
        "container": "results_in_div",

        // An element which will be completely emptied and filled as the searches happen.
        "results": "search_results_div",

        // A full template of how an individual result should appear.  Elements with "data-field" attributes will have
        // their contents replaced as needed.  The value of "data-field" should match a field in the response JSON.
        "template": "search_result_template_div",

        // A full template with content which represents no search results.  This will be copied into
        // "search_results_div" as needed.
        "no_results_template": "search_no_result_template_div",
    },
}

function srch_add_result(item_to_add, _result_style) {
    for (const template_element of srch_get_result_element_template(_result_style)) {
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
function srch_convert_values_to_query_string(values_to_send) {
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
    if (srch_key_is_visible(e)){
        srch_start_timer(e.target);
    } else if (!srch_key_is_not_visible(e)) {
        srch_start_timer(e.target);
    }
}
function srch_get_href_args(e) {
    /*
    Returns the data attributes of element e which are named "data-href-arg-*".
    <a ... data-href-arg-order="x" data-href-arg-line-item="y">
    returns {"order": "x", "line-item": "y"}
    */
    const attributes = {};
    for (let i = 0; i < e.attributes.length; i++) {
        const attribute = e.attributes[i];
        if (attribute.name.startsWith('data-href-arg-')) {
            attributes[attribute.name.slice(14)] = attribute.value;
        }
    }
    return attributes;
}
function srch_get_no_result_element_template(_result_style) {
    // The root of the template used for indicating no results.
    return document.getElementById(result_style_ids[_result_style]["no_results_template"]);
}
function srch_get_result_element(_result_style) {
    // The root of the container element for search results.
    // TODO: This needs to handle form-named fields.  "{{ widget.attrs.id }}-search-results-div"
    return document.getElementById(result_style_ids[_result_style]["results"]);
}
function srch_get_result_element_template(_result_style) {
    // The root of the template used for individual search results.  Always an array even if there is only one element.
    if (Array.isArray(result_style_ids[_result_style]["template"])) {
        let _srch_result_element_template = [];
        for (const id of result_style_ids[_result_style]["template"]) {
            _srch_result_element_template.push(document.getElementById(id));
        }
        return _srch_result_element_template;
    }
    return [document.getElementById(result_style_ids[_result_style]["template"])];
}
function srch_get_search_elements() {
    console.log(`srch_get_search_elements for srch_form_id = "${srch_form_id}"`);
    const form = document.getElementById(srch_form_id);
    return form.querySelectorAll("[data-search-field]");
}
function srch_get_values_to_send() {
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
    window.clearTimeout(srch_keypress_timer);
}
function srch_key_is_not_visible(e) {
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
    for (const _result_style of active_result_styles) {
        srch_remove_all_results(_result_style);
        let new_result = srch_get_no_result_element_template(_result_style).cloneNode(true);
        srch_get_result_element(_result_style).appendChild(new_result);
        new_result.style.display = "";  // "unsetting" display so it inherits rather than forcing 'block' or 'inline-block'
    }
}
function srch_populate_results(data_packet) {
    // console.log(`srch_populate_results(echo=...)`);
    // console.log(data_packet.echo);
    if (data_packet.data.length === 0) {
        srch_no_results();
        return;
    }
    for (const _result_style of active_result_styles) {
        srch_remove_all_results(_result_style);
        for (const item of data_packet.data) {
            srch_add_result(item, _result_style);
        }
    }
    srch_post_popultate_results.detail = data_packet.echo;
    document.dispatchEvent(srch_post_popultate_results);
}
function srch_remove_all_results(_result_style) {
    // Clears any existing search results in preparation for either "No results" or new elements.

    // remove any events added to search results.  Replaces the controller since it is a fire-once thing.
    srch_abort_controller.abort();
    srch_abort_controller = new AbortController();

    let _srch_results_element = srch_get_result_element(_result_style);
    if (_srch_results_element.firstChild === null) {
        return;
    }
    while( _srch_results_element.firstChild ){
        _srch_results_element.removeChild( _srch_results_element.firstChild );
    }
}
function srch_setup_events() {
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
    window.clearTimeout(srch_keypress_timer);
    srch_keypress_timer = setTimeout(() => {
        srch_timer_elapsed_func(e);
    }, 750);
}
function srch_timer_elapsed_func(caller_obj) {
    let values_to_send = srch_get_values_to_send();
    if (values_to_send.empty) {
        srch_no_results();
        return;
    }
    console.log(caller_obj);
    if (caller_obj.hasAttributes("id")) {
        values_to_send["echo"] = {"id": caller_obj.id};
    }
    let query_string = srch_convert_values_to_query_string(values_to_send)
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
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
    srch_setup_events();
    srch_no_results();
});
