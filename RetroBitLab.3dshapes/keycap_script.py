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
    
    # Dynamic printable area (70% of top surface dimensions)
    key_w = bbox.XMax - bbox.XMin
    key_h = bbox.ZMax - bbox.ZMin
    MAX_W = key_w * 0.7
    MAX_H = key_h * 0.7
    print(f"DEBUG: Keycap surface: {key_w:.2f}x{key_h:.2f}mm, Max legend area: {MAX_W:.2f}x{MAX_H:.2f}mm")

    # 3. Parsing Legend
    legend = legend.replace("\\n", "\n").replace("\\t", "\t")
    lines = [l.strip() for l in legend.split("\n") if l.strip()]
    
    font_size = 7.0
    line_spacing_factor = 1.4
    min_scale = 1.0

    def get_seg_info(seg):
        if seg.startswith("\\R") or seg.startswith("\R"):
            return True, seg[2:]
        return False, seg

    # 3a. Global Scaling Calculation
    total_block_w = 0
    for line in lines:
        row_seg_w = 0
        segments = [s for s in line.split("\t") if s]
        for seg in segments:
            is_rev, text = get_seg_info(seg)
            s_obj = Draft.makeShapeString(String=text, FontFile=font_path, Size=font_size)
            sw = s_obj.Shape.BoundBox.XMax - s_obj.Shape.BoundBox.XMin
            if is_rev: sw += 1.0
            row_seg_w += sw
            doc.removeObject(s_obj.Name)
        
        min_gap = 1.5
        required_w = row_seg_w + min_gap * (len(segments)-1)
        if required_w > MAX_W:
            s = MAX_W / required_w
            if s < min_scale: min_scale = s
        if required_w > total_block_w: total_block_w = required_w

    if (len(lines) * font_size * line_spacing_factor) > MAX_H:
        s = MAX_H / (len(lines) * font_size * line_spacing_factor)
        if s < min_scale: min_scale = s

    # 4. Generate 2D Shapes with Justification
    all_2d_shapes = []
    for i, line in enumerate(lines):
        segments = [s for s in line.split("\t") if s]
        N = len(segments)
        line_segs = []
        total_seg_w = 0
        
        for seg in segments:
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
            
            w = sh.BoundBox.XMax - sh.BoundBox.XMin
            line_segs.append({'shape': sh, 'width': w})
            total_seg_w += w

        if N > 1:
            gap = (MAX_W - total_seg_w) / (N - 1)
            curr_x = -MAX_W / 2
            for seg_data in line_segs:
                sh = seg_data['shape']
                sh.translate(App.Vector(curr_x - sh.BoundBox.XMin, -i * font_size * min_scale * line_spacing_factor, 0))
                all_2d_shapes.append(sh)
                curr_x += seg_data['width'] + gap
        else:
            sh = line_segs[0]['shape']
            sh.translate(App.Vector(-line_segs[0]['width']/2 - sh.BoundBox.XMin, -i * font_size * min_scale * line_spacing_factor, 0))
            all_2d_shapes.append(sh)

    # 5. Transform and Extrude individually
    temp_comp = Part.makeCompound(all_2d_shapes)
    btb = temp_comp.BoundBox
    block_cy = (btb.YMax + btb.YMin) / 2
    
    all_solids = []
    for sh in all_2d_shapes:
        # Vertical center of block
        sh.translate(App.Vector(0, -block_cy, 0))
        # Rotate to TOP face: -90 on X is the standard non-mirrored orientation
        sh.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        # Position EXACTLY at y_top (no offset to avoid protrusion)
        sh.translate(App.Vector(c_x, y_top, c_z))
        # Extrude DOWN into the keycap
        solid_piece = sh.extrude(App.Vector(0, -1.1, 0))
        all_solids.append(solid_piece)

    # 6. Boolean Operations
    full_tool = Part.makeCompound(all_solids)
    try:
        keycap_with_hole = keycap_solid.cut(full_tool)
    except:
        keycap_with_hole = keycap_solid
        
    try:
        legend_infill = full_tool.common(keycap_solid)
        if not legend_infill.Faces: legend_infill = full_tool
    except:
        legend_infill = full_tool

    # 7. Export
    ok = doc.addObject("Part::Feature", "Keycap"); ok.Shape = keycap_with_hole
    ol = doc.addObject("Part::Feature", "Legend"); ol.Shape = legend_infill
    Import.export([ok, ol], output_path)
    print(f"SUCCESS: {output_path} generated (Corrected Orientation & Flush).")

except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
sys.exit(0)
