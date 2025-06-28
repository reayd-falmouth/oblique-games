// vertex.glsl
varying vec2 v_text;

vec4 position(mat4 transform_projection, vec4 vertex_position) {
    // Use the built‐in texture coordinate provided by Love2D.
    v_text = VertexTexCoord.xy;
    return transform_projection * vertex_position;
}
