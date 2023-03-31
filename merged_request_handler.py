import json
import sqlite3
import base64
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO

IMAGE_DATABASE = '/var/jail/home/team78/project/merged_image.db'


editing_html = ''' <img id="image" width=""></img>\
            <p>\
            \
            <label for="saturation">Saturation: </label>-100 \
            <input type="range" id="saturation" name="saturation" min="-100" in="0">100</input>\
            \
            <p>\
            \
            <label for="brightness">Brightness: </label>-100\
            <input type="range" id="brightness" name="brightness" min="-100" in="0">100</input>\
            \
            <p>\
            \
            <label for="exposure">Exposure: </label>-100\
            <input type="range" id="exposure" name="exposure" min="-100" value="0">100</input>\
            \
            <p>\
            \
            <label for="vibrance">Vibrance: </label>-100\
            <input type="range" id="vibrance" name="vibrance" min="-100" value="0">100</input>\
            \
            <p>\
            \
            <label for="sharpness">Sharpness: </label>0\
            <input type="range" id="sharpness" name="sharpness" in="0" value = "0">100</input>\
            \
            <p>\
            \
            <label for="noise">Noise: </label>0\
            <input type="range" id="noise" name="noise" value="0" in="0">100</input>\
            \
            <p>\
            \
            <label for="noise">Hue: </label>0\
            <input type="range" id="hue" name="hue" value="0" in="0">100</input>\
            \
            <p>\
            \
            <label for="noise">Blur: </label>0\
            <input type="range" id="blur" name="blur" value="0" in="0">100</input>\
            \
            \
            <p>\
            <button onclick="clear_image()">clear</button>\
            <button onclick="submit_image()">submit</button>\
'''

get_elements = '\
                var sat = document.getElementById("saturation"); \n\
                var bright = document.getElementById("brightness");\n\
                var sharp = document.getElementById("sharpness");\n\
                var exposure = document.getElementById("exposure");\n\
                var curr_edit_image = document.getElementById("image");\n\
                var noise = document.getElementById("noise");\n\
                var vibrance = document.getElementById("vibrance");\n\
                var hue = document.getElementById("hue");\n\
                var blur = document.getElementById("blur");\n\
                var buttons = document.getElementsByClassName("image_button"); \n\
                '


clear_image = 'function clear_image(){\n\
                    Caman(curr_edit_image, function() { \n\
                      this.revert();\n\
                      this.render();\n\
                    }); \n\
                    sat.value = 0; bright.value = 0; sharp.value = 0; exposure.value = 0;\n\
                    noise.value = 0; vibrance.value = 0; blur.value = 0; hue.value = 0;\n\
                }'


get_gif_images = '''
    var all_images = []; //array of all the images, organized by name and each version of name
    var curr_frame = []; //keeps track of img frame atm
    
    for(let i = 0; i < buttons.length; i++){
        var all_versions = [];
        var curr_name = buttons[i].getAttribute("data");
        //console.log("curr name, "+curr_name);
        var images_this_version = document.getElementsByClassName(curr_name);
        
        for(let j = 0; j < images_this_version.length; j++){
            img = images_this_version[j];
            all_versions.push(img.src);
        }
        all_images.push(all_versions);
        curr_frame.push(0);
        
    }
    console.log(all_images);
    console.log(curr_frame);
'''

animate_gif_images = '''
    window.setInterval(animate, 500); //500 milliseconds
    function animate(){
        for(let i = 0; i < curr_frame.length; i++){
            curr_frame[i] += 1;
            if (curr_frame[i] === (all_images[i].length ) ){ //exceeded num versions 
                curr_frame[i] = 0;
            }
            new_src = all_images[i][ curr_frame[i] ];
            buttons[i].getElementsByTagName("img")[0].src = new_src;
            
        } 
    }

'''
apply_filters = '$("input[type=range]").change(applyFilters);\n\
                \n\
                function applyFilters() {\n\
                    Caman(curr_edit_image, function() { \n\
                      this.revert();\n\
                      this.render();\n\
                      this.height = this.height;\n\
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


button_style = ".image_button{padding:0; border:0; background:0;}"


def request_handler(request):
    if request['method'] == 'GET':
        connection, cursor = get_db_cursor()
        if "ID" not in request['values']:
            raise Exception('The ID must be specified.')
        else:
            id = request['values']['ID']
        
        string = f'''
        <!DOCTYPE html>
        <style>
            {button_style}
        </style>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/camanjs/3.3.0/caman.full.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.js" integrity="sha512-n/4gHW3atM3QqRcbCn6ewmpxcLAHGaDjpEBu4xZd47N0W2oQ+6q7oc3PXstrJYXcbNU1OHdQ1T7pAP+gi5Yu8g==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
        <html>
            <body>
                <div id = "image_display" style="text-align:center; font-family: Arial;">
                Click Any Image to Start!<p>
        '''

        if 'name' in request['values']:
            rows = get_rows_by_id_and_image_name(
                cursor, id, request['values']['name'])

        else:
            rows = get_rows_by_id(cursor, id)

        for row in rows:

            if row[3] == 1:  # the first version is what contains gif
                # the img contains that images version, the button contains the highest version to SUBMIT AS
                highest_version = int(
                    get_highest_version(cursor, id, row[2])[3]) + 1
                print(highest_version)

                string += "<button class=\"image_button\"data=\"{name}\"data-value=\"{data}\" version=\"{highest_version}\">\n".format(
                    name=str(row[2]), highest_version=str(highest_version), data=row[1])
                string += '<img class="{name}" src="data:image/jpeg;base64,{data}" data="{data}" version="{version}" width ="250px">\n'.format(
                    data=row[1], name=str(row[2]), version=str(row[3]))
                string += '</button>\n'

            else:  # they don't show but are here for extracting sources
                string += '<img class="{name}" src="data:image/jpeg;base64,{data}" data="{data}" version="{version}" style ="display:none">\n'.format(
                    data=row[1], name=str(row[2]), version=str(row[3]))

        connection.close()

        submit_image = 'function submit_image(){\n'
        submit_image += 'var new_image = ""; \n'
        submit_image += 'Caman(curr_edit_image, function() { \n'
        submit_image += 'new_image = String(this.toBase64()); \n'
        submit_image += 'new_image = this.canvas.toDataURL("image/jpeg"); \n'
        submit_image += 'new_image = new_image.split(",")[1];\n'
        submit_image += '}); \n'
        submit_image += 'console.log(curr_edit_image.data+" "+curr_edit_image.version);'
        submit_image += 'var settings = { \n'
        submit_image += '"url": "https://608dev-2.net/sandbox/sc/team78/project/merged_request_handler.py?ID='\
                        + id+'&name="+curr_edit_image.data+"&version="+curr_edit_image.version, \n'
        submit_image += '"method": "POST", \n'
        submit_image += '"timeout": 0, \n'
        submit_image += '"headers": { \n'
        submit_image += '"Content-Type": "application/json" }, \n'
        submit_image += '"data": new_image, \n'
        submit_image += '}; \n'
        submit_image += 'console.log(settings["url"]);'
        submit_image += '$.ajax(settings).done(function (response) { \n'
        submit_image += 'console.log(response); \n'
        submit_image += '}); \n'
        submit_image += "const Http = new XMLHttpRequest();\n"
        submit_image += "const url='https://608dev-2.net/sandbox/sc/team78/project/merged_request_handler.py?ID="+id
        if 'name' in request['values']:
            submit_image += "&name="+request['values']['name']
        
        submit_image += "'; \n"
        submit_image += '''
            setTimeout(function() {
                window.location.replace(url); 
            }, 1000); //2000 ms = 2sec
            '''
        submit_image += '}'

        string += "</p></div>\n"
        string += '<div id = "image_editing" style = "display:none; text-align:center;font-family:arial;">'+editing_html+'</div>'
        string += "</body> <script>\n" + get_elements + "\n"
        string += " buttons = document.getElementsByClassName(\"image_button\");\n"
        string += " display = document.getElementById(\"image_display\");\n"
        string += ' var n = ""; var v = ""; \n'
        string += " editing = document.getElementById(\"image_editing\");\n"

        string += "$(buttons).click(function(){\n "
        string += 'curr_edit_image.data = this.getAttribute("data"); \n'
        string += 'curr_edit_image.version = this.getAttribute("version"); \n'
        string += 'n, v = this.getAttribute("data-value"), this.getAttribute("version"); \n'

        string += 'curr_edit_image.src = "data:image/jpeg;base64,"+this.getAttribute("data-value");\n'

        string += "display.style.display = \"none\"; \n"
        string += "editing.style.display = \"block\";\n"
        string += "}); \n"
        string += get_gif_images + "\n" + animate_gif_images + "\n"
        string += clear_image + "\n" + apply_filters + "\n" + submit_image + "\n"
        string += "</script> </html>"
        return string
    elif request['method'] == 'POST':
        connection, cursor = get_db_cursor()
        if "ID" not in request['values']:
            raise Exception('The ID must be specified.')
        else:
            id = request['values']['ID']

        if 'name' not in request['values']:
            img_name = get_highest_name(cursor, id)
            if img_name == None:
                img_name = 1
            else:
                img_name = img_name+1

            img_version = 1
        else:
            img_name = request['values']['name']
            try:
                img_version = request['values']['version']
            except:
                raise Exception(
                    "image name was passed in without a specified version")

        img_data = request['data'][:]
        if 'filter' in request['values']:
            filter = request['values']['filter']
            image = base64_pil(img_data)
            if filter == "bw":
                converted_image = image.convert('L')
            elif filter == "emboss":
                converted_image = image.filter(ImageFilter.EMBOSS)
            elif filter == "contour":
                converted_image = image.filter(ImageFilter.CONTOUR)
            elif filter == "edges":
                converted_image = image.filter(ImageFilter.FIND_EDGES)
            elif filter == "min":
                converted_image = image.filter(ImageFilter.MinFilter(9))
            elif filter == "max":
                converted_image = image.filter(ImageFilter.MaxFilter(9))

            base64_image = pil_base64(converted_image)
            insert(cursor, request['values']['ID'],
                   base64_image, img_name, img_version)
        else:
            im = base64_pil(img_data)
            base64_string = pil_base64(im)
            insert(cursor, request['values']['ID'],
                   base64_string, img_name, img_version)

        values = cursor.execute(
            '''SELECT name, version FROM image_table;''').fetchall()

        connection.commit()
        connection.close()
        return values

    elif request['method'] == 'PUT':
        if "ID" not in request['values']:
            raise Exception('The ID must be specified.')
        else:
            id = request['values']['ID']

        if "name" not in request['values']:
            raise Exception('The name must be specified.')
        else:
            name = request['values']['name']

        connection, cursor = get_db_cursor()
        result = get_highest_version(cursor, id, name)
        if result == None:
            return f'No image with the name {name}'

        (id, base64_image, name, version) = result
        if request['data'] != b'':
            body = json.loads(request['data'])
            if 'changes' in body:
                image = base64_pil(base64_image)
                draw = ImageDraw.Draw(image)
                changed = False
                for change in body['changes']:
                    if change['shape'] == 'ellipse':
                        x = int(change['x']) // 128 * 320
                        y = int(change['y']) // 160 * 240
                        width = int(change['width'])
                        height = int(change['height'])
                        color = tuple(change['color']) if 'color' in change else (
                            0, 0, 255)
                        draw.ellipse([(x - width // 2, y - height // 2),
                                     (x + width // 2, y + height // 2)], fill=color)
                        changed = True
                    elif change['shape'] == 'rect':
                        x = int(change['x'])
                        y = int(change['y'])
                        width = int(change['width'])
                        height = int(change['height'])
                        color = tuple(change['color']) if 'color' in change else (
                            0, 0, 255)
                        draw.rectangle(
                            [(x, y), (x + width, y + height)], fill=color)
                        changed = True
                    elif change['shape'] == 'points':
                        points = []
                        for point in change['points']:
                            points.append((point['x'], point['y']))

                        color = tuple(change['color']) if 'color' in change else (
                            0, 0, 255)
                        draw.point(points, fill=color)
                        changed = True

                if changed:
                    insert(cursor, id, pil_base64(image), name, version + 1)

            connection.commit()
            connection.close()
            return 'done'
        else:
            return 'no body'


def get_db_cursor():
    connection = sqlite3.connect(IMAGE_DATABASE)
    create_table(connection.cursor())
    return connection, connection.cursor()


def create_table(cursor):
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS image_table (id text, img text, name integer, version integer);''')


def get_rows_by_id(cursor, id):
    return cursor.execute(
        '''SELECT * FROM image_table WHERE id = ?;''', (id,)).fetchall()


def get_rows_by_id_and_image_name(cursor, id, name):
    return cursor.execute(
        '''SELECT * FROM image_table WHERE id = ? AND name = ?;''', (id, name)).fetchall()


def get_highest_name(cursor, id):
    return cursor.execute(
        '''SELECT MAX(name) FROM image_table WHERE id = ?;''', (id,)).fetchone()[0]


def insert(cursor, id, image, name, version):
    cursor.execute('''INSERT into image_table (id, img, name, version) VALUES (?, ?, ?, ?);''',
                   (id, image, name, version))


def get_highest_version(cursor, id, name):
    return cursor.execute('''SELECT * FROM image_table WHERE id=? AND name=? ORDER BY version DESC;''', (id, name)).fetchone()


def base64_pil(base64_str):
    image = base64.b64decode(base64_str)
    image = BytesIO(image)
    image = Image.open(image)
    return image


def pil_base64(image):
    img_buffer = BytesIO()
    image.save(img_buffer, format='JPEG')
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode('UTF-8')
    return base64_str
