let add_activity_form = document.forms.add_activity;
let activities_table = document.querySelector('table[class~=activities-table]');
let activities_list = document.querySelector('div[class~=activities-list]');

add_activity_form.addEventListener('submit', add_activity);

async function add_activity (event) {
    event.preventDefault();
    const csrftoken = getCookie('csrftoken');

    let fetch_url = window.location.origin + '/ru/api/v1/activities/';

    let form_data = new FormData(add_activity_form);

    let response = await fetch(fetch_url, {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    })

    let result = await response.json();

    console.log(result);

    if (result.message) {
        alert_massage(result.message, 'success');
    }

    if (result.errors) {
        for (let error_name in result.errors) {
            let error = result.errors[error_name];
            alert_massage(error, 'danger', 10);
        }
    } else {
        insert_tr_in_activities_table(result);
        update_activities_html_list(result);
    }
}

function insert_tr_in_activities_table (data) {
    let activities_table_tbody = activities_table.querySelector('tbody');

    let new_tr = document.createElement('tr');

    new_tr.append(
        create_new_td(data.title)
    );

    let color_square_div = document.createElement('div');
    color_square_div.classList.add('color-square');
    color_square_div.style.backgroundColor = data.color;
    let color_td = create_new_td('');
    color_td.append(color_square_div);

    new_tr.append(
        color_td
    );

    new_tr.append(
        create_new_td(data.parent)
    );

    new_tr.append(
        create_new_td(data.total_time)
    );

    activities_table_tbody.append(new_tr);
}

function create_new_td (content) {
    let td = document.createElement('td');
    td.textContent = content;
    return td;
}

function update_activities_html_list (data) {

    new_activities_list = activities_list.cloneNode();

    for (let branch of data.activities_html_list) {
        let new_div = document.createElement('div');
        new_div.classList.add('col-lg-3');
        new_div.innerHTML = branch;

        new_activities_list.append(new_div);
    }

    activities_list.replaceWith(new_activities_list);
}
