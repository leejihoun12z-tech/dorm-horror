// 시안: 손전등 안 = 낮 그림, 손전등 밖(어둠) = "진짜 모습"이 희미하게 빛남.
shader_type spatial;
render_mode cull_disabled, depth_draw_opaque;

uniform sampler2D tex_day : source_color, filter_linear_mipmap;
uniform sampler2D tex_true : source_color, filter_linear_mipmap;
uniform vec3 flash_pos = vec3(0.0);
uniform vec3 flash_dir = vec3(0.0, 0.0, -1.0);
uniform float cos_in = 0.94;
uniform float cos_out = 0.915;
uniform float true_glow = 0.55;

varying vec3 wpos;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec4 d = texture(tex_day, UV);
	vec4 t = texture(tex_true, UV);
	float c = dot(normalize(wpos - flash_pos), normalize(flash_dir));
	float n = fract(sin(dot(floor(UV * vec2(40.0, 80.0)), vec2(12.9898, 78.233))) * 43758.5453);
	float m = smoothstep(cos_out, cos_in, c + (n - 0.5) * 0.012);
	vec4 col = mix(t, d, m);
	if (col.a < 0.5) {
		discard;
	}
	ALBEDO = col.rgb;
	EMISSION = (1.0 - m) * t.rgb * true_glow;
	ROUGHNESS = 1.0;
}
