from .models import Activities
from django.utils.html import mark_safe, format_html
from django.shortcuts import reverse

def get_childs_if_node_is_parent_else_return_node(node, user):
    if not node.childs.filter(user=user):
        return f'''<li 
                        data-color="{node.color}" style="color: {node.color}"
                        data-activity_id="{node.id}"
                        data-title="{node.title}"
                        data-parent="{node.parent}"
                        data-bs-toggle="modal"
                        data-bs-target="#activity-modal"
                    >
                    {node.title}
                    </li>'''
    if not node.childs.filter(user=user) and node.number == node.parent.childs.filter(user=user).count():
        return f'''<li 
                        data-color="{node.color}" style="color: {node.color}"
                        data-activity_id="{node.id}"
                        data-title="{node.title}"
                        data-parent="{node.parent}"
                        data-bs-toggle="modal"
                        data-bs-target="#activity-modal"
                    >
                    {node.title}
                    </li></ul>'''
    else:
        return f'''<li 
                        data-color="{node.color}" style="color: {node.color}"
                        data-activity_id="{node.id}"
                        data-title="{node.title}"
                        data-parent="{node.parent}"
                        data-bs-toggle="modal"
                        data-bs-target="#activity-modal"
                    >
                    {node.title}
                    </li><ul>''' + ''.join([get_childs_if_node_is_parent_else_return_node(child_node, user) for child_node in node.childs.filter(user=user)]) + '</ul>'

def activities_list(user):
    basic_activities = Activities.objects.filter(user=user, parent=None)
    node_tree = []
    for node in basic_activities:
        node_tree.append(mark_safe('<ul class="activities-tree">' + get_childs_if_node_is_parent_else_return_node(node, user) + '</ul>'))
    return node_tree

class HTMLPagination:
    def __init__(self, page, url_name):
        self.page = page
        self.paginator = page.paginator
        self.url_name = url_name

    def get_page_range(self):

        page_range = self.paginator.get_elided_page_range(
            self.page.number,
            on_each_side=7,
            on_ends=0,
        )
        page_range = list(page_range)
        for i in range(page_range.count('…')):
            page_range.remove('…')

        return page_range

    def get_pagination_unit(self, href, content, li_class=''):
        return format_html(
            '<li class="page-item {}"><a class="page-link" href="{}">{}</a></li>',
            li_class,
            href,
            mark_safe(content),
        )

    def get_pagination_content(self):
        base_url = reverse(self.url_name)
        content = []

        if self.page.has_previous():
            if self.page.previous_page_number() > 4:
                content.append(
                    self.get_pagination_unit(
                        base_url + f'?page={1}',
                        '<i class="bi bi-caret-left-fill"></i>'
                    )
                )

            content.append(
                self.get_pagination_unit(
                    base_url + f'?page={self.page.previous_page_number()}',
                    '<i class="bi bi-caret-left"></i>'
                )
            )

        page_range = self.get_page_range()

        for page_number in page_range:
            if page_number == self.page.number:
                content.append(
                    self.get_pagination_unit(
                        base_url + f'?page={page_number}',
                        page_number,
                        'active',
                    )
                )
            else:
                content.append(
                    self.get_pagination_unit(
                        base_url + f'?page={page_number}',
                        page_number,
                    )
                )

        if self.page.has_next():
            content.append(
                self.get_pagination_unit(
                    base_url + f'?page={self.page.next_page_number()}',
                    '<i class="bi bi-caret-right"></i>'
                )
            )

            if self.page.next_page_number() + 4 < self.paginator.num_pages:
                content.append(
                    self.get_pagination_unit(
                        base_url + f'?page={self.paginator.num_pages}',
                        '<i class="bi bi-caret-right-fill"></i>'
                    )
                )

        return mark_safe(''.join(content))

    def get_pagination(self):
        return format_html(
            '''
            <nav aria-label="Page navigation example">
                <ul class="pagination justify-content-center">
                {}
                </ul>
            </nav>
            ''',
            self.get_pagination_content()
        )

    def __str__(self):
        if self.page.has_other_pages():
            return self.get_pagination()
        else:
            return ''
