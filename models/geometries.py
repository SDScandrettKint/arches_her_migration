from convertbng.cutil import convert_bng, convert_lonlat
import logging
import re
import inspect

logging.basicConfig(filename='migration_geometries.log', filemode='a+', format='%(asctime)s - %(message)s', level=logging.DEBUG)

class GeometryConversion:

    def do_geom_conversion(point_input, line_input, poly_input):
        if point_input:
            GeometryConversion.point_geom(point_input)
        if poly_input:
            GeometryConversion.poly_geom(poly_input)
        if line_input:
            GeometryConversion.line_geom(line_input)


    def point_geom(value):
        all_nums = [float(s) for s in re.findall(r"[-+]?(?:\d*\.*\d+)", value)]
        longlatlist = []
        for easting, northing in zip(*[iter(all_nums)]*2):
            newcoords = convert_lonlat([easting], [northing]) # gives tuple
            pair_list = []
            for tuple_item in newcoords:
                for each in tuple_item:
                    pair_list.append(each)
            longlatlist.append(pair_list)
        
        if len(longlatlist) > 1: # multipoint
            point_type = "MULTIPOINT"
            GeometryConversion.individual_formatting(longlatlist, point_type)
        else:
            point_type = "POINT"
            GeometryConversion.individual_formatting(longlatlist, point_type)



    def line_geom(value):
        all_nums = [float(s) for s in re.findall(r"[-+]?(?:\d*\.*\d+)", value)]

    def poly_geom(value):
        all_nums = [float(s) for s in re.findall(r"[-+]?(?:\d*\.*\d+)", value)]


    def individual_formatting(value_list, geom_type):
        print("this will be for formatting point or lines or multi versions before going into overall")
        type_list = ["POINT", "MULTIPOINT", "LINESTRING", "MULTILINESTRING", "POLYGON", "MULTIPOLYGON"]
        if geom_type in type_list:
            if geom_type == "POINT":
                inner_coords = value_list[0]
                coords_as_str = " ".join(str(x) for x in inner_coords) 
                point_str = "POINT (%s)" % (coords_as_str)
            else:
                point_str = None
            
            if geom_type == "MULTIPOINT":
                multipoint_coords_list = []
                for inner_coords in type_list:
                    coords_as_str = " ".join(str(x) for x in inner_coords)
                    bracketed = "(%s)" % (" ".join(str(x) for x in inner_coords))
                    multipoint_coords_list.append(bracketed)
                multipoint_str = "MULTIPOINT (%s)" % (", ".join(str(x) for x in multipoint_coords_list))
            else:
                multipoint_str = None

        else:
            logging.warning("The following type, %s, doesn't exist in available types. Is it misspelt?" % (geom_type))

        GeometryConversion.final_format(point_str, multipoint_str, f_line=None, f_multiline=None, f_poly=None, f_multipoly=None)




    def final_format(f_point, f_multipoint, f_line, f_multiline, f_poly, f_multipoly):
        print("as name suggests this will be final geom with GEOMETRYCOLLECTION at start")
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        print(args,values)
