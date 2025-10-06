function model_picker_copy_to(el) {
    // Copy the selected item's information to the specified fields.
    for (const element of el.querySelectorAll("[data-copy-to]")) {
        document.getElementById(element.dataset.copyTo).value = element.innerText;
    }
}

function model_picker_onclick(e) {
    // What was this supposed to fix?
    let closest = e.target.closest('.search_result_clicky');
    // e.target == might be the <span> which was clicked?
    // closest == should be the <a> containing the clicked <span>
    console.log("model_picker_onclick")
    console.log(e.target);
    console.log(closest);
    if (closest && document.getElementById("search_results_div").contains(closest)) {
        model_picker_copy_to(closest);
        model_picker_hide_dropdown();
    }
}

function model_picker_delayed_hide_dropdown(e) {
    setTimeout(model_picker_hide_dropdown.bind(null, e), 500);
}

function model_picker_hide_dropdown(e) {
    console.log(`model_picker_hide_dropdown(e):`)
    console.log(e);
    // e.target is the specific dropdown which triggered the hide
    // need to find that specific dropdown's dropdown-content to hide.  Cannot assume [0].
    document.getElementsByClassName("dropdown-content")[0].style.display = "";
}

function model_picker_show_dropdown(e) {
    console.log(`model_picker_show_dropdown(e):`)
    console.log(e);
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

(function() {
    // onload based on https://stackoverflow.com/a/9899701
    // TODO: Will automatically calling the setup events cause issues?  Does this style of 'onload' behave differently in a .js as it does in the main .html?
    model_picker_setup_events();
})();
