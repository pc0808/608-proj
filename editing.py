import sqlite3

database = "/var/jail/home/team78/project/image.db" #location of sophie's database

get_elements = '\
                var sat = document.getElementById("saturation"); \n\
                var bright = document.getElementById("brightness");\n\
                var pix = document.getElementById("pixelize");\n\
                var sharp = document.getElementById("sharpness");\n\
                var exposure = document.getElementById("exposure");\n\
                var image = document.getElementById("image");\n\
                var noise = document.getElementById("noise");\n\
                var vibrance = document.getElementById("vibrance");\n\
                var hue = document.getElementById("hue");\n\
                var blur = document.getElementById("blur");\n\
                '    



clear_image = 'function clear_image(){\n\
                    Caman(image, function() { \n\
                      this.revert();\n\
                      this.render();\n\
                    }); \n\
                    sat.value = 0; bright.value = 0; sharp.value = 0; exposure.value = 0;\n\
                    noise.value = 0; vibrance.value = 0; blur.value = 0; hue.value = 0;\n\
                }'
    
    
apply_filters = '$("input[type=range]").change(applyFilters);\n\
                \n\
                function applyFilters() {\n\
                    Caman(image, function() { \n\
                      this.revert();\n\
                      this.render();\n\
                      this.brightness(bright.value).render();\n\
                      this.exposure(exposure.value).render();\n\
                      this.saturation(sat.value).render();\n\
                      this.sharpen(sharp.value).render();\n\
                      this.noise(noise.value).render();\n\
                      this.vibrance(vibrance.value).render();\n\
                      this.hue(hue.value).render();\n\
                      this.stackBlur(blur.value).render();\n\
                    }); \n\
                }'
                                              
def request_handler(request):
    if request["method"] == "POST":
        ## SHOWS THE PHOTO GALLERY --> not sure if we will do it by user or by all 
        ##integrate with sophie later on 
        
        return "Not valid method"
    elif request["method"] == "GET":
        
        try:
            user = request['values']['user']
            image_name = int(request['values']['name'])
            version =  int(request['values']['version'])
        except Exception as e:
            return "Not an existing image or user data given"
        
        conn = sqlite3.connect(database)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # make cursor into database (allows us to execute commands)
        things = c.execute('''SELECT * FROM image_table WHERE id = (?) AND name = (?) ORDER BY version ASC;''', (user,image_name)).fetchall()
        last_version = 0
        for row in things:
            if row[3] == version: 
                base64_message = row[1]
            if row[3] > last_version: last_version = row[3]
            
        version = last_version+1 #version we are submitting as 
        conn.close() # close connection to database
        
        
        button_class = '.button{color:blue;}'
        entireThing = ".entireThing{text-align:center;font-family:arial;}"
        labelStyle = ".label{font-weight:bold;}"
    

        submit_image = 'function submit_image(){\n'
        submit_image += 'var new_image = ""; \n'
        submit_image += 'Caman(image, function() { \n'
        submit_image += 'new_image = String(this.toBase64()); \n'
        submit_image += 'new_image = this.canvas.toDataURL("image/jpeg");'
        submit_image += 'new_image = new_image.split(",")[1];\n'
        submit_image += '}); \n'
        submit_image += 'var settings = { \n'
        submit_image += '"url": "https://608dev-2.net/sandbox/sc/team78/project/request_handler.py?ID='\
                        +user+'&img='+str(image_name)+'&version='+str(version)+'", \n'
        submit_image += '"method": "POST", \n'

        submit_image += '"timeout": 0, \n'
        submit_image += '"headers": { \n'
        submit_image += '"Content-Type": "application/json" }, \n'
        submit_image += '"data": new_image, \n'
        submit_image += '}; \n'
        submit_image += 'console.log(settings["data"]);'
        submit_image += '$.ajax(settings).done(function (response) { \n'
        submit_image += 'console.log(response); \n'
        submit_image += '}); \n'
        submit_image += '}'
                            

                           
        string = f'''<!DOCTYPE html>
        <style>
            {button_class}
            {entireThing}
            {labelStyle}
        </style>
        <html> 
            <body>
                <div class="entireThing">
                    <img id="image" src = "data:image/png;base64,{base64_message}"></img>
                    <p>
                
                    <label for="saturation">Saturation: </label>-100
                    <input type="range" id="saturation" name="saturation" min="-100" in="0">100</input>
                    
                    <p>
                    
                    <label for="brightness">Brightness: </label>-100
                    <input type="range" id="brightness" name="brightness" min="-100" in="0">100</input>
                    
                    <p>
                    
                    <label for="exposure">Exposure: </label>-100
                    <input type="range" id="exposure" name="exposure" min="-100" value="0">100</input>
                    
                    <p>
                    
                    <label for="vibrance">Vibrance: </label>-100
                    <input type="range" id="vibrance" name="vibrance" min="-100" value="0">100</input>
                    
                    <p>
                    
                    <label for="sharpness">Sharpness: </label>0
                    <input type="range" id="sharpness" name="sharpness" in="0" value = "0">100</input>
                    
                    <p>
                    
                    <label for="noise">Noise: </label>0
                    <input type="range" id="noise" name="noise" value="0" in="0">100</input>
                    
                    <p>
                    
                    <label for="noise">Hue: </label>0
                    <input type="range" id="hue" name="hue" value="0" in="0">100</input>
                    
                    <p>
                    
                    <label for="noise">Blur: </label>0
                    <input type="range" id="blur" name="blur" value="0" in="0">100</input>
                    
                    <p>
                    
                    <label for="pixelize">Pixelize? </label>
                    <input type="checkbox" id="pixelize" name="pixelize"in="0"></input>
                    
                    
                <p>
                <button onclick="clear_image()">clear</button>
                <button onclick="submit_image()">submit</button>
                </div>
            </body>
            <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/camanjs/3.3.0/caman.full.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.js" integrity="sha512-n/4gHW3atM3QqRcbCn6ewmpxcLAHGaDjpEBu4xZd47N0W2oQ+6q7oc3PXstrJYXcbNU1OHdQ1T7pAP+gi5Yu8g==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
            <script>
                {get_elements}
                {apply_filters}
                {clear_image}
                {submit_image}
                
            
            </script>
        </html>
        '''
        return string
    
    


