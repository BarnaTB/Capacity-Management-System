from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    """Custom JSON Renderer class to reformat the JSON response adding the `data`
    field so as to align with the JSend specification

    See: https://github.com/omniti-labs/jsend

    Args:
        JSONRenderer (BaseRenderer): Default JSONRenderer class from DRF

    Returns:
        ByteString: A byte-string representation of the `data` in the JSON
        response
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Check if the response is successful
        if renderer_context is not None:
            response = renderer_context["response"]
            if response.status_code < 400:
                # Add the "data" and "status" keys for successful responses
                data = {"data": data, "status": "success"}

        # Call the base render method to serialize the data
        return super().render(data, accepted_media_type, renderer_context)
