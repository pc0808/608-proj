def request_handler(request):
    if request["method"] == "POST":
        base64 = request["data"]
        
        string = f''''<!DOCTYPE html>
        <html> 
            <body>
            <image width ="500px" src = "data:image/png;base64,{base64}">
            </body>
        </html>
        '''
        
        return string