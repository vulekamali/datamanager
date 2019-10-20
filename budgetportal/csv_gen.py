import csv
from django.http import StreamingHttpResponse


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def generate_csv_response(data):
    """
    :param data: dict
    :return: StreamingHttpResponse object

    Roughly based on https://docs.djangoproject.com/en/2.1/howto/outputting-csv/#streaming-large-csv-files
    """
    response = StreamingHttpResponse(
        streaming_content=iter_items(data["cells"], Echo()), content_type="text/csv"
    )
    response["Content-Disposition"] = 'attachment; filename="vulekamali-download.csv"'

    return response


def iter_items(cells, pseudo_buffer):
    headers_list = list(cells[0].keys())
    headers_dict = {}
    writer = csv.DictWriter(pseudo_buffer, fieldnames=sorted(headers_list))

    # Not using writer.writeheader because it's not working - not sure why
    for header in headers_list:
        headers_dict[header] = header
    yield writer.writerow(headers_dict)

    for dict_object in cells:
        yield writer.writerow(dict_object)
