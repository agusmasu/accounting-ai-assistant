import functions_framework

@functions_framework.http
def test_function(request):
    """A simple test function to verify that Cloud Functions can be built correctly."""
    return {"status": "success", "message": "Test function is working!"} 