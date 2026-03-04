import os
import sys
import FreeCAD as App
import Part
import Draft
import Import

print("INFO: Script started.")

legend = os.getenv("IN_TEXT", "")
step_path = os.getenv("IN_STEP", "")
font_path = os.getenv("IN_FONT", "")
output_path = os.getenv("OUT_STEP")

try:
    doc = App.newDocument("DoubleShot")
    
    # 1. Load Base Geometry
    raw_shape = Part.Shape()
    raw_shape.read(step_path)
    keycap_solid = sorted(raw_shape.Solids, key=lambda s: s.Volume, reverse=True)[0] if raw_shape.Solids else Part.makeSolid(raw_shape)

    # 2. Keycap Analysis
    bbox = keycap_solid.BoundBox
    y_top = bbox.YMax
    c_x, c_z = (bbox.XMax + bbox.XMin) / 2, (bbox.ZMax + bbox.ZMin) / 2

    # 3. Parsing Legend
    legend = legend.replace("\\n", "\n").replace("\\t", "\t")
    lines = [l.strip() for l in legend.split("\n") if l.strip()]
    
    font_size = 7.0
    min_scale = 1.0
    MAX_DIM = 12.0

    def get_seg_info(seg):
        if seg.startswith("\\R") or seg.startswith("\R"):
            return True, seg[2:]
        return False, seg

    # Calculate global scale
    for line in lines:
        row_w = 0
        segments = line.split("\t")
        for i, seg in enumerate(segments):
            if not seg: continue
            is_rev, text = get_seg_info(seg)
            s_obj = Draft.makeShapeString(String=text, FontFile=font_path, Size=font_size)
            sw = s_obj.Shape.BoundBox.XMax - s_obj.Shape.BoundBox.XMin
            if is_rev: sw += 1.5
            row_w += sw
            if i < len(segments) - 1: row_w += 4.5
            doc.removeObject(s_obj.Name)
        if row_w > MAX_DIM:
            s = (MAX_DIM / row_w) * 0.95
            if s < min_scale: min_scale = s

    # 4. Generate 2D Shapes and find block center
    all_2d_shapes = []
    for i, line in enumerate(lines):
        curr_x = 0
        segments = line.split("\t")
        for j, seg in enumerate(segments):
            if not seg: continue
            is_rev, text = get_seg_info(seg)
            s_obj = Draft.makeShapeString(String=text, FontFile=font_path, Size=font_size)
            sh = s_obj.Shape.copy()
            doc.removeObject(s_obj.Name)
            
            if min_scale < 1.0:
                m = App.Matrix(); m.scale(min_scale, min_scale, min_scale); sh.transformShape(m)
            
            if is_rev:
                tb = sh.BoundBox
                marg = 0.5 * min_scale
                rw, rh = (tb.XMax - tb.XMin) + 2*marg, (tb.YMax - tb.YMin) + 2*marg
                rect = Part.makePlane(rw, rh, App.Vector(tb.XMin - marg, tb.YMin - marg, 0))
                sh = rect.cut(sh)
            
            sh.translate(App.Vector(curr_x - sh.BoundBox.XMin, -i * font_size * min_scale * 1.3, 0))
            all_2d_shapes.append(sh)
            curr_x += (sh.BoundBox.XMax - sh.BoundBox.XMin)
            if j < len(segments) - 1: curr_x += 4.5 * min_scale

    # 5. Transform and Extrude individually
    # Calculate block center for 2D shapes
    temp_comp = Part.makeCompound(all_2d_shapes)
    btb = temp_comp.BoundBox
    block_cx = (btb.XMax + btb.XMin) / 2
    block_cy = (btb.YMax + btb.YMin) / 2
    
    all_solids = []
    for sh in all_2d_shapes:
        # Center the piece relative to the whole block center
        sh.translate(App.Vector(-block_cx, -block_cy, 0))
        
        # Rotate -90 on X: Front of text (Z+) faces Up (+Y), Top of text (Y+) faces Back (-Z)
        # This is the correct, non-mirrored orientation for the top face
        sh.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        
        # Move to the keycap surface
        sh.translate(App.Vector(c_x, y_top + 0.01, c_z))
        
        # Extrude DOWN into the keycap (Global Y negative)
        solid_piece = sh.extrude(App.Vector(0, -1.1, 0))
        all_solids.append(solid_piece)

    # 6. Boolean Operations
    full_tool = Part.makeCompound(all_solids)
    keycap_with_hole = keycap_solid.cut(full_tool)
    legend_infill = full_tool.common(keycap_solid)
    if not legend_infill.Faces:
        legend_infill = full_tool

    # 7. Export
    ok = doc.addObject("Part::Feature", "Keycap"); ok.Shape = keycap_with_hole
    ol = doc.addObject("Part::Feature", "Legend"); ol.Shape = legend_infill
    Import.export([ok, ol], output_path)
    print(f"SUCCESS: {output_path} generated correctly.")

except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
sys.exit(0)
