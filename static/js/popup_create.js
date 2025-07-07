/*
Expects an <a> tag formed like the following:
    <a class="my-pop-up" href="{% url "inventory:category_create" %}"
       data-control="{{ form.category.id_for_label }}" data-refresh-url="{% url "inventory:api_category" %}">
        <img src="{% static "admin/img/icon-addlink.svg" %}" alt="" width="18" height="18">
    </a>
class="my-pop-up" is used to find the tags and attach event handlers.
href is the create url for the object.
data-control is the id of the select control to refresh.
data-refresh-url points to an API which returns a JSON of all of the objects.

For visible values more complex than a single field, use the function, refresh_visible_fn.
    refresh_visible_fn = function(e) {
        return `${e["amount"]} ${e["unit"]}`;
    }
It receives a single object from the list returned by the data-refresh-url API from the <a> tag.  You can use whatever
logic needed along with formatting.  Just so long as a single string is returned.
 */

// Used to find the <a> tags
var popup_class_name = "my-pop-up";
// Controls the popup window features.
var popup_properties = "height=250,width=600,resizable=yes,scrollbars=yes";
// Was "{{request.scheme}}://{{request.get_host}}" but can't do that here.
var expected_origin = "http://localhost:8000";
// A flag added to the popup's querystring so the view can tell it is in a popup and hide/show as appropriate.
var popup_queryparam_flag = "_popup";
// The id field in the API response when refreshing the <select>.
var refresh_id_field = "id";
// The visible field in the API response when refreshing the <select>.  Ignored if refresh_visible_fn is set.
var refresh_visible_field = "name";
// function which will be passed an object from the data-refresh-url result.  As string is expected.
var refresh_visible_fn = null;

let refresh_because_of_popup = null;
let refresh_popup_url = null;

function popup_create_setup() {
    for (const el of document.getElementsByClassName(popup_class_name)) {
        el.addEventListener("click", popup_event);
    }
    // The CategoryCreateView calls "window.opener.postMessage" which triggers a "message" event.
    window.addEventListener("message", handle_popup_close);
}
function popup_event(e) {
    e.preventDefault();
    let a_tag = e.target.parentNode;
    refresh_because_of_popup = document.getElementById(a_tag.dataset.control);
    refresh_popup_url = a_tag.dataset.refreshUrl;
    const href = new URL(a_tag.href);
    href.searchParams.set(popup_queryparam_flag, 1);
    const win = window.open(href, "What's in a name?", popup_properties);
    win.focus();
}
async function handle_popup_close(e) {
    if (e.origin !== expected_origin) return;
    let new_id = JSON.parse(e.data);
    const response = await fetch(refresh_popup_url);
    const refreshed_data = await response.json();

    // empty the select control of all options.
    refresh_because_of_popup.innerHTML = "";
    refreshed_data.forEach((e, i) => {
        let is_selected = "";
        if (e[refresh_id_field] === new_id.id) {
            is_selected = " selected";
        }
        let visible_string = "";
        if (refresh_visible_fn == null) {
            visible_string = e[refresh_visible_field];
        } else {
            visible_string = refresh_visible_fn(e);
        }
        refresh_because_of_popup.appendChild(
            generateElements(`<option value="${e[refresh_id_field]}"${is_selected}>${visible_string}</option>`)[0]);
    });
}
