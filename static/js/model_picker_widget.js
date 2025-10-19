function model_picker_copy_to(el) {
    // Copy the selected item's information to the specified fields.
    for (const element of el.querySelectorAll("[data-copy-to]")) {
        // find elements that exactly match the copyTo id.  Need to catch in case no element found.
        let copy_to_element = document.getElementById(element.dataset.copyTo);
        if (copy_to_element) {
            copy_to_element.value = element.innerText;
        } else {
            console.log(`Did not find "${element.dataset.copyTo}".`);
            // TODO: find elements which have a prepended field name; "id_source_item-item_name"
            // id_source_item is the hidden <input> in the model picker widget.
            // item_name is the id specified in copyTo
        }
    }
}

function model_picker_copy_to_selected(source_element, selected_element) {
    // copies data from source_element to selected_element.
    // source_element == a.search_result_clicky.  <a> tag that contains the <spans> which have
    // OR, this is the dict created from the <a> tag.  This is to handle initial forms which haven't done a search.
    if (selected_element) {
        // iterate over data-id in selected_element and find matching in e.target's data-field
        let source_item_data = model_picker_get_item_data(source_element);
        for (const di of selected_element.querySelectorAll("[data-id]")) {
            di.innerHTML = source_item_data[di.dataset.id];
        }
    }
}

function model_picker_get_form_prefix(mp_top_level) {
    /*
    * Given the top-level element of a ModePicker widget, find the hidden input field and figure out the form_prefix, if
    * any.
    * */
    /*
    Formset:
    class="hidden_model_picker" id="id_line_items-0-source_item" name="line_items-0-source_item"
    class="dropbtn model_picker" id="id_line_items-0-source_item-search-wider"
    Want: "id_line_items-0-"

    Form w/o prefix:
    class="hidden_model_picker" id="id_source_item" name="source_item"
    class="dropbtn model_picker" id="id_source_item-search-wider"
    Want: ""

    Mixed - and _ in the prefix.  Unlikely to happen but should handle it.
    Form w/ prefix "billy-bob_thornton":
    class="hidden_model_picker" id="id_billy-bob_thornton-source_item" name="billy-bob_thornton-source_item"
    class="dropbtn model_picker" id="id_billy-bob_thornton-source_item-search-wider"
    Want: "billy-bob_thornton"
     */
    if (isFormset(mp_top_level)) {
        throw new Error("NotImplementedError: Using ModePickerWidget in a formset is not supported at this time.");
    }
    let hidden_mp = mp_top_level.querySelector(".hidden_model_picker");
    // TODO: incomplete.  left here as a starting point if I ever need to get the form_prefix dynamically.
}

function model_picker_get_item_data(element) {
    // element is a.search_result_clicky
    let source_item_data = {}
    for (const df of element.querySelectorAll("[data-field]")) {
        source_item_data[df.dataset.field] = df.innerHTML;
    }
    return source_item_data;
}

function model_picker_get_selected_element(widget_element = null) {
    // widget_element is the outer-most <div> for the control.  Nothing of the control should be outside so this is a
    // safe place to start .querySelector calls.
    if (widget_element) {
        return widget_element.querySelector(".dropdown-selected");
    }
    let first_widget = document.getElementById(srch_form_id).querySelector(".dropdown");
    return first_widget.querySelector(".dropdown-selected");
}

function model_picker_get_top_level(e) {
    /*
    * Get the top-level form field parent of the element `e`.  This is the containing div in the widget.  Not an INPUT
    * element.
    * */
    return e.closest(".dropdown");
}
function model_picker_onclick(e) {
    // e.target is a.search_result_clicky
    model_picker_copy_to(e.target);
    model_picker_copy_to_selected(e.target, model_picker_get_selected_element(e.detail.widget_element));
    model_picker_hide_dropdown();
    getNextTabStop(model_picker_get_top_level(e.target).querySelector(".model_picker")).focus();
}

function model_picker_delayed_hide_dropdown(e) {
    setTimeout(model_picker_hide_dropdown.bind(null, e), 500);
}

function model_picker_hide_dropdown(e) {
    // e.target is the specific dropdown which triggered the hide
    // need to find that specific dropdown's dropdown-content to hide.  Cannot assume [0].
    document.getElementsByClassName("dropdown-content")[0].style.display = "";
}

function model_picker_refresh_selected() {
    /*
    const result_element = document.getElementById(e.detail.result_element_id);
    const container = result_element.closest(".dropdown");
    const input_element = container.querySelector(".model_picker");
    const selected_template = document.getElementById(input_element.dataset.selectedTemplateId);
    console.log(selected_template);
    */
    const form = document.getElementById(srch_form_id);
    for (const mp_element of form.querySelectorAll(".model_picker")) {
        let mp_top_level = model_picker_get_top_level(mp_element);
        let hidden_mp_element = mp_top_level.querySelector(".hidden_model_picker");
        let selected_div = document.getElementById(mp_element.dataset.selectedDiv);
        let selected_template = document.getElementById(mp_element.dataset.selectedTemplateId);
        let new_result = selected_template.cloneNode(true);
        selected_div.appendChild(new_result);
        for (let element of new_result.querySelectorAll("[data-id]")) {
            // adjust id of element.  Should use widget's id as part to handle multiple model_pickers;
            element.id = `${hidden_mp_element.id}-${element.dataset.id}`;
        }
        // unwraps the template container from the actual template.  Just doing this so there isn't a useless layer.
        new_result.replaceWith(...new_result.childNodes);
    }
}

function model_picker_reset_required_attributes() {
    // Django sets the required flag on the visible input element.  It should be on the hidden element.
    const form = document.getElementById(srch_form_id);
    Array.from(form.querySelectorAll(".model_picker")).map((e) => e.required = false);
    Array.from(form.querySelectorAll(".hidden_model_picker")).map((e) => e.required = true);
}

function model_picker_show_dropdown(e) {
    // e.target is the specific dropdown which triggered the show
    // need to find that specific dropdown's dropdown-content to show.  Cannot assume [0].
    document.getElementsByClassName("dropdown-content")[0].style.display = "block";
}

function model_picker_setup_events() {
    // the user clicked an item in the drop down.
    document.addEventListener(srch_result_onclick_name, model_picker_onclick);

    for (const element of document.getElementsByClassName("model_picker")) {
        // the user clicked or tabbed out of the search text box.  Have to delay the hiding as clicking a dropdown item
        // causes the focusout and that event gets processed first.  Hiding immediately prevents the click from processing.
        element.addEventListener('focusout', model_picker_delayed_hide_dropdown);

        // the user clicked or tabbed into the search text box.
        element.addEventListener('focusin', model_picker_show_dropdown);
    }
    // the search completed and has finished populating the dropdown.  Just in case it wasn't visible already, show the
    // dropdown.
    document.addEventListener(srch_post_populate_results_name, model_picker_show_dropdown);
}

ready(() => {
    model_picker_setup_events();
    model_picker_reset_required_attributes();
    model_picker_refresh_selected();
});
