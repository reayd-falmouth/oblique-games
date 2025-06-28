// pixel.glsl
uniform vec2 texSize;
uniform float brightness;

varying vec2 v_text;

vec4 effect(vec4 color, Image texture, vec2 texture_coords, vec2 screen_coords) {
    // Use the vertex-provided coordinate.
    vec2 center = vec2(0.5, 0.5);
    vec2 off_center = v_text - center;

    // Apply non-linear distortion.
    off_center *= 1.0 + 0.3 * pow(abs(off_center.yx), vec2(2.5));
    vec2 new_coords = center + off_center;

    // Define a border margin for smoothing.
    float border = 0.05;
    float xFade = smoothstep(0.0, border, new_coords.x) * smoothstep(0.0, border, 1.0 - new_coords.x);
    float yFade = smoothstep(0.0, border, new_coords.y) * smoothstep(0.0, border, 1.0 - new_coords.y);
    float edgeFactor = xFade * yFade;

    if (edgeFactor <= 0.0) {
        return vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        // Sample the texture at the distorted coordinates.
        vec4 texColor = texture2D(texture, new_coords);
        texColor.rgb *= brightness;

        // Apply the scanline effect.
        // A lower thicknessFactor (e.g. 0.05) will make the dark bands thicker and more visible.
        float thicknessFactor = 0.1;
        float fv = fract(new_coords.y * texSize.y * thicknessFactor);
        fv = min(1.0, 0.8 + 0.5 * min(fv, 1.0 - fv));
        texColor.rgb *= fv;

        return texColor * edgeFactor * color;
    }
}
