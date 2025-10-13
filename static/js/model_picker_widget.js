function model_picker_copy_to(el) {
    // Copy the selected item's information to the specified fields.
    for (const element of el.querySelectorAll("[data-copy-to]")) {
        // find elements that exactly match the copyTo id.  Need to catch in case no element found.
        document.getElementById(element.dataset.copyTo).value = element.innerText;
        // find elements which have a prepended field name; "id_source_item-item_name"
        // id_source_item is the hidden <input> in the model picker widget.
        // item_name is the id specified in copyTo

    }
}

function model_picker_onclick(e) {
    // might just call this once.  model_picker_refresh_selected(e);
    model_picker_copy_to(e.target);
    model_picker_hide_dropdown();
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
    console.log("model_picker_refresh_selected");
    /*
    const result_element = document.getElementById(e.detail.result_element_id);
    const container = result_element.closest(".dropdown");
    const input_element = container.querySelector(".model_picker");
    const selected_template = document.getElementById(input_element.dataset.selectedTemplateId);
    console.log(selected_template);
    */
    const form = document.getElementById(srch_form_id);
    for (const mp_element of form.querySelectorAll(".model_picker")) {
        console.log(mp_element);
        let hidden_mp_element = mp_element.closest(".dropdown").querySelector(".hidden_model_picker");
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
    model_picker_refresh_selected();
});
