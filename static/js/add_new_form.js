var form_name = "set this to the overall name of the form fields.  i.e. line_items, items, etc.";
var after_add_focus_suffix = "set this from page as it will likely be different for each use.";
var line_item_position_id = "line_item_position";
var formset_container_id = "set this to the id of the table or list that contains the forms.  No #";
var copy_from_previous = "list of fields to copy from previous form";

function add_new_form(focus_suffix="") {
    let new_form = create_new_form(focus_suffix);
    append_new_form(new_form);
    let total_forms_element = get_total_forms_element();
    let total_forms_value = get_total_forms_value(total_forms_element);
    total_forms_element.value = total_forms_value + 1;
    focus_after_add(new_form, focus_suffix);
    copy_values_from_previous(total_forms_element.value);
}

function append_new_form(new_form) {
    let formset_container = get_formset_container();
    formset_container.appendChild(new_form);
    new_form.style.display = "";
}

function clone_empty_form() {
    let empty_form = get_formset_container().querySelector("#empty-form").cloneNode(true);
    empty_form.removeAttribute("id");
    return empty_form;
}

function copy_values_from_previous(total_forms_value) {
    if (total_forms_value === 0) {
        return;
    }
    if (getType(copy_from_previous) !== "array") {
        return;
    }
    let prev_form_num = total_forms_value - 1;
    for (const field of copy_from_previous) {
        let prev_key = `id_${form_name}-${prev_form_num}-${field}`;
        let cur_key = `id_${form_name}-${total_forms_value}-${field}`;
        document.getElementById(cur_key).value = document.getElementById(prev_key).value;
    }
}

function create_new_form(focus_suffix="") {
    let new_form = clone_empty_form();
    let total_forms_element = get_total_forms_element();
    let total_forms_value = get_total_forms_value(total_forms_element);
    new_form.setAttribute("data-form-number", total_forms_value);
    for (const el of new_form.querySelectorAll('input, label, select, textarea, div, ul')) {
        modify_element(el, total_forms_value);
    }
    new_form.classList.remove("empty-form");
    return new_form;
}

function focus_after_add(new_form, focus_suffix) {
    if (focus_suffix === "") {
        return;
    }
    let focus_after_add_id = "";
    for (const el of new_form.querySelectorAll('input, label, select, textarea, div, ul')) {
        if (el.id.endsWith(focus_suffix)){
            focus_after_add_id = el.id;
        }
    }
    console.log(`focus_after_add, focus_suffix="${focus_suffix}", focus_after_add_id="${focus_after_add_id}"`);
    if (focus_after_add_id !== "") {
        document.getElementById(focus_after_add_id).focus();
    }
}

function get_formset_container(){
    return document.getElementById(formset_container_id);
}

function get_total_forms_element() {
    return document.getElementById(`id_${form_name}-TOTAL_FORMS`);
}

function get_total_forms_value(total_forms_element) {
    return parseInt(total_forms_element.value);
}

function modify_element(el, form_number) {
    console.log(el);
    let to_edit_attributes = ['id', 'name', 'for', 'aria-labelledby']
    if ((el.type === 'number') && (el.id.endsWith(`-${line_item_position_id}`))) {
        el.value = form_number + 1;
    }
    for (const attribute of to_edit_attributes) {
        if (el.hasAttribute(attribute)) {
            let old_value = el.getAttribute(attribute);
            let new_value = old_value.replace(/__prefix__/g, form_number);
            el.setAttribute(attribute, new_value);
        }
    }
}

function add_new_form_link_onclick(e) {
    console.log("add_new_form_link_onclick");
    console.log(e);
    // e.preventDefault();
    add_new_form(after_add_focus_suffix);
    return false; // prevents the browser from following link?  I thought that is what e.preventDefault() was for.
}
