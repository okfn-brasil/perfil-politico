from django.core.paginator import Paginator

from restless.dj import DjangoResource


class ApiResource(DjangoResource):
    per_page = 10

    def wrap_list_response(self, data):
        return {
            "objects": data,
            "per_page": self.paginator.per_page,
            "count": self.paginator.count,
            "num_page": self.paginator.num_pages,
            "page": self.page,
        }

    def paginate(self, queryset, per_page=None):
        if per_page is None:
            per_page = self.per_page

        self.paginator = Paginator(queryset, per_page)

        self.page = int(self.request.GET.get("page", 1))
