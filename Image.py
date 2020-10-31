def read_rows(path,origin_x,origin_y,height,width):
    import struct
    global bmp_w
    global bmp_h
    image_file = open(path, "rb")
    image_file.seek(18,0)
    bmp_w = struct.unpack('I',image_file.read(4))[0]
    print(f'Width of image : {bmp_w} px')
    diff = (bmp_w*3)%4
    if diff != 0:
        bmp_w +=diff
    bmp_h = struct.unpack('I',image_file.read(4))[0]
    print(f'Height of image : {bmp_h} px')
    print(f'Total number of subpixels : {bmp_w*bmp_h*3} pixels')
    image_file.seek(54,0)
    
    
    
    if origin_x+width > bmp_w or origin_y+height > bmp_h:
        raise ValueError(f'Dimensions are outside the figure size, choose between {bmp_w}x{bmp_h} pixels')
        
        return
    # We need to read pixels in as rows to later swap the order
    # since BMP stores pixels starting at the bottom left.
    test_rows = []
    test_row = []
    pixel_index = 0

    while True:
        if pixel_index == bmp_w:
            pixel_index = 0
            test_rows.append(test_row)
            if len(test_row) != bmp_w * 3:
                raise Exception(f'Row length is not {bmp_w*3} but {str(len(row))}/3.0 = {str(len(row))}/ 3.0)')
            test_row = []
        pixel_index += 1

        r_string = image_file.read(1)
        g_string = image_file.read(1)
        b_string = image_file.read(1)

        if len(r_string) == 0:
            # This is expected to happen when we've read everything.
            if len(test_rows) != bmp_h:
                print (f"Warning!!! Read to the end of the file at the correct sub-pixel (red) but we've not read {bmp_h} rows!")
            break

        if len(g_string) == 0:
            print( "Warning!!! Got 0 length string for green. Breaking.")
            break

        if len(b_string) == 0:
            print ("Warning!!! Got 0 length string for blue. Breaking.")
            break
        
        test_row.append(r_string)
        test_row.append(g_string)
        test_row.append(b_string)

    image_file.close()
    print(f'Number of rows : {len(test_rows)}')
    return test_rows



def repack_sub_pixels(test_rows,origin_x,origin_y,height,width):
    print ("Repacking pixels...")
    test_sub_pixels = []
    diff = (width*3)%4
    padding = 0
        

    for jdx, test_row in enumerate(test_rows):
        if jdx >= origin_y and jdx <origin_y+height:
            for idx , sub_pixel in enumerate(test_row):
                if idx >= (origin_x*3) and idx< ((origin_x+width)*3):
                    test_sub_pixels.append(sub_pixel)
            if (diff!= 0):
                pad = 0
                pad = pad.to_bytes(1, 'little')
                for x in range(diff):
                    test_sub_pixels.append(pad)
                    test_sub_pixels.append(pad)
                    test_sub_pixels.append(pad)
                padding = diff

    print (f'Packed {len(test_sub_pixels)} sub-pixels including padding: i.e {width+diff}x{height}x3 pixels.')
    
    return test_sub_pixels,padding

def get_header(file_name,w,h,p,tsp,on):
    li = []
    print(f'Total Padding done: {p*3} bytes')
    bmp = open(file_name, 'rb')
    Type =  bmp.read(2)
    Size = bmp.read(4) #change
    Reserved_1 = bmp.read(2)
    Reserved_2 = bmp.read(2)
    Offset = bmp.read(4)
    DIB_Header_Size = bmp.read(4)
    Width = bmp.read(4) 
    Height = bmp.read(4) 
    Colour_Planes = bmp.read(2)
    Bits_per_Pixel = bmp.read(2)
    Compression_Method = bmp.read(4)
    Raw_Image_Size = bmp.read(4)
    Horizontal_Resolution = bmp.read(4)
    Vertical_Resolution = bmp.read(4)
    Number_of_Colours = bmp.read(4)
    Important_Colours = bmp.read(4)
    bmp.close()
    Width = w.to_bytes(4, 'little')
    Height = h.to_bytes(4, 'little')
    Raw_Image_Size = (((w+p)*3)*h).to_bytes(4,'little')
    Size = ((((w+p)*3)*h)+54).to_bytes(4, 'little')
    li.append(Type)
    li.append(Size)
    li.append(Reserved_1)
    li.append(Reserved_2)
    li.append(Offset)
    li.append(DIB_Header_Size)
    li.append(Width)
    li.append(Height)
    li.append(Colour_Planes)
    li.append(Bits_per_Pixel)
    li.append(Compression_Method)
    li.append(Raw_Image_Size)
    li.append(Horizontal_Resolution)
    li.append(Vertical_Resolution)
    li.append(Number_of_Colours)
    li.append(Important_Colours)
    for x in tsp:
        li.append(x)
    with open(f'./{on}', 'wb') as file:
        for x in li:
            file.write(x)
        
    file.close

def crop(file_name,output_name,a,b,h,w):
    '''
    Takes input file name ,
    output file name, 
    origin x from left  , 
    origin y from top , 
    height of cropped image from origin , 
    width of cropped image from origin.
    '''
    test_rows = read_rows(file_name,a,b,h,w)
    test_sub_pixels,padding = repack_sub_pixels(test_rows,a,b,h,w)
    dim = int((len(test_sub_pixels))//h) 
    w = dim//3
    print(f'length of columns : {dim} ')
    print(f'New width of image with padding: {w}')
    print(f'New height of image: {h}')

    get_header(file_name,w,h,padding,test_sub_pixels,output_name)
    print('Image Saved')

'''

CALL FUNCTION HERE

'''
while(1):
    
    p1,p2,p3,p4,p5,p6 = input('To Crop the Image, Enter in following format input_filename,output_filename,origin_x,origin_y,height,width\n').split(sep=',')
    p3 = int(p3)
    p4 = int(p4)
    p5 = int(p5)
    p6 = int(p6)
    crop(p1,p2,p3,p4,p5,p6 )
