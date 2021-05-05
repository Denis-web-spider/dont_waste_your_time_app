'use strict';

let menu_button = document.querySelector('header .menu');

menu_button.addEventListener('click', toggle_menu);

set_menu_height();
adjust_main_section();

function set_menu_height () {
    let keep = document.querySelector('section.main .keep');

    let li_height = keep.querySelector('li').offsetHeight;
    let count_li =  keep.querySelectorAll('li').length;

    keep.parentNode.style.height = li_height * count_li + 'px';
}

function toggle_menu (event) {
    let target = event.target;

    let keep = document.querySelector('section.main .keep');
    keep.classList.toggle('show');
    if (keep.classList.contains('show')) {
        adjust_main_section(350);
    } else {
        adjust_main_section();
    }
}

function adjust_main_section (width) {
    let main_section = document.querySelector('.main-section');

    let header_height = document.querySelector('header').offsetHeight;
    let side_menu_width;
    if (!width) {
        side_menu_width = document.querySelector('.main').offsetWidth;
    } else {
        side_menu_width = width;
    }

    main_section.style.paddingLeft = side_menu_width + 'px';
    main_section.style.paddingTop = header_height + 'px';
}

// Вспомогательные функции
let z_index = 100;
function alert_massage (message, status, delay=3.5) {
    let container_fluid = document.createElement('div');
    container_fluid.classList.add('container-fluid');
    container_fluid.style.position = 'fixed';
    container_fluid.style.zIndex = z_index;
    container_fluid.style.marginTop = '50px';

    z_index += 1;

    let row = document.createElement('div');
    row.classList.add('row');
    container_fluid.append(row);

    let col = document.createElement('div');
    col.classList.add('col-md-8');
    col.classList.add('offset-md-2');
    col.classList.add('text-center');
    row.append(col);

    let alert = document.createElement('div');
    alert.classList.add('alert');
    alert.classList.add('alert-' + status);
    alert.classList.add('alert-dismissible');
    alert.classList.add('fade');
    alert.classList.add('show');
    alert.setAttribute('role', 'alert');
    col.append(alert);

    alert.innerHTML = message;

    let close_button = document.createElement('button');
    close_button.classList.add('btn-close');
    close_button.setAttribute('type', 'button');
    close_button.setAttribute('data-bs-dismiss', 'alert');
    close_button.setAttribute('aria-label', 'Close');
    alert.append(close_button);

    document.body.prepend(container_fluid);

    new Promise(function (resolve, reject) {
        setTimeout(delete_alert, delay * 1000);
    })

    function delete_alert () {
        let click_event = new Event('click', { bubbles: true, cancelable: true });
        close_button.dispatchEvent(click_event);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
